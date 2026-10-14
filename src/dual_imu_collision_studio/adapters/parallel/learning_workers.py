"""Windows spawn execution; all optimization and threshold choices stay in Learning."""

from __future__ import annotations

import multiprocessing
from multiprocessing.connection import wait
import math
import os
from types import SimpleNamespace

import psutil

from dual_imu_collision_studio.domain.learning.model import (
    ExecutionBatch,
    HardwareMemoryInsufficientError,
    HistoryExecutionError,
)


def _read_memory():
    memory = psutil.virtual_memory()
    total, available = memory.total, memory.available
    if (
        not math.isfinite(total)
        or not math.isfinite(available)
        or total <= 0
        or available <= 0
        or available > total
    ):
        raise HistoryExecutionError(
            "Hardware memory availability could not be measured; check execution environment"
        )
    return total, available


def _fold_worker(dataset, job):
    from dual_imu_collision_studio.domain.learning.service import LearningService

    from dual_imu_collision_studio.domain.learning.self_imu import service_for_dataset

    return service_for_dataset(dataset).evaluate_fold_job(dataset, job)


def _recording_worker(_dataset, job):
    from dual_imu_collision_studio.domain.learning.service import LearningService
    from dual_imu_collision_studio.domain.learning.model import RecordingJob

    recordings, models, scores = _dataset
    restored = RecordingJob(
        job.job_index,
        recordings[job.recording_key],
        models[job.model_key],
        job.numeric_type,
        job.config,
        scores[job.score_key],
    )
    return LearningService().evaluate_recording_job(restored)


def _batch_process(dataset, connection, worker):
    try:
        while True:
            job = connection.recv()
            if job is None:
                return
            try:
                result = worker(dataset, job)
                connection.send(("result", result))
            except MemoryError as exc:
                connection.send(("failure", "memory", str(exc) or "MemoryError"))
                return
            except InterruptedError as exc:
                connection.send(("failure", "cancelled", str(exc)))
                return
            except Exception as exc:
                connection.send(
                    ("failure", "execution", f"{type(exc).__name__}: {exc}")
                )
                return
    except (EOFError, BrokenPipeError):
        return
    finally:
        connection.close()


class SpawnLearningExecutor:
    """One bounded batch at a time; no nested pools and no worker retries."""

    def __init__(
        self, *, fold_worker=_fold_worker, maximum_ram_fraction=0.90, training_workers=1
    ):
        if not 0 < maximum_ram_fraction <= 1:
            raise ValueError("Invalid memory admission fraction")
        if type(training_workers) is not int or not 1 <= training_workers <= 8:
            raise ValueError("Training workers must be an integer from 1 to 8")
        self._training_workers = training_workers
        self._fold_worker = fold_worker
        self._maximum_ram_fraction = maximum_ram_fraction

    def configure_training_workers(self, count):
        """Configure the next run; the composition owner calls this only while idle."""
        if type(count) is not int or not 1 <= count <= 8:
            raise ValueError("Training workers must be an integer from 1 to 8")
        self._training_workers = count

    def evaluate_folds(self, dataset, jobs, progress=None, cancelled=None):
        return self._execute(dataset, jobs, self._fold_worker, 8, progress, cancelled)

    def evaluate_recordings(self, jobs, cancelled=None):
        # Copy each recording/model/score array once per worker, not per threshold.
        recordings = {id(j.recording): j.recording for j in jobs}
        models = {id(j.model): j.model for j in jobs}
        scores = {id(j.scores): j.scores for j in jobs}
        payloads = tuple(
            SimpleNamespace(
                job_index=j.job_index,
                recording_key=id(j.recording),
                model_key=id(j.model),
                score_key=id(j.scores),
                numeric_type=j.numeric_type,
                config=j.config,
            )
            for j in jobs
        )
        return self._execute(
            (recordings, models, scores),
            payloads,
            _recording_worker,
            4,
            None,
            cancelled,
        )

    def _execute(self, dataset, jobs, worker, capacity, progress, cancelled):
        if not jobs:
            return ExecutionBatch(())
        ids = [j.job_index for j in jobs]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate job identities")
        stop = cancelled or (lambda: False)
        publish = progress or (lambda *_: None)

        _, launch_available = _read_memory()
        # Training count is captured explicitly; Qualification retains its cap of four.
        if worker is self._fold_worker:
            capacity = min(capacity, self._training_workers)
        memory_diagnostics = ()
        context = multiprocessing.get_context("spawn")
        active = {}
        children = []
        results = {}
        pending = iter(jobs)
        peak = 0

        def check_resources():
            nonlocal peak
            if stop():
                raise InterruptedError("Learning cancelled")
            rss = psutil.Process().memory_info().rss
            for process, _connection in children:
                try:
                    rss += psutil.Process(process.pid).memory_info().rss
                except psutil.NoSuchProcess:
                    pass
            peak = max(peak, rss)
            current_total, current_available = _read_memory()
            occupied = current_total - current_available
            current_ceiling = current_total * self._maximum_ram_fraction
            if occupied > current_ceiling:
                raise HardwareMemoryInsufficientError(
                    "Learning stopped: system memory usage exceeds ceiling; "
                    f"occupied={occupied} bytes, total={current_total} bytes, "
                    f"available={current_available} bytes, "
                    f"ceiling={current_ceiling:.0f} bytes "
                    f"({self._maximum_ram_fraction:.0%})"
                )

        try:
            for _ in range(min(capacity, len(jobs))):
                check_resources()
                parent, child = context.Pipe()
                process = context.Process(
                    target=_batch_process,
                    args=(dataset, child, worker),
                    name="dual-imu-learning",
                )
                try:
                    process.start()
                except Exception as exc:
                    parent.close()
                    if process.pid is not None:
                        if process.is_alive():
                            process.terminate()
                        process.join(timeout=2)
                    if (
                        isinstance(exc, MemoryError)
                        or isinstance(exc, OSError)
                        and getattr(exc, "winerror", None) in {8, 14, 1455}
                    ):
                        raise HardwareMemoryInsufficientError(
                            "Hardware memory is insufficient; Learning stopped"
                        ) from exc
                    raise HistoryExecutionError(
                        f"Worker startup failed; check hardware/execution environment: {exc}"
                    ) from exc
                finally:
                    child.close()
                children.append((process, parent))
                job = next(pending)
                parent.send(job)
                active[parent] = (process, job.job_index)
            while active:
                check_resources()
                ready = wait(tuple(active), timeout=0.02)
                for connection in ready:
                    process, identity = active[connection]
                    try:
                        message = connection.recv()
                    except (EOFError, OSError) as exc:
                        raise HistoryExecutionError(
                            f"Worker exited without result (exit {process.exitcode}); check hardware/execution environment"
                        ) from exc
                    if message[0] == "failure":
                        if message[1] == "memory":
                            raise HardwareMemoryInsufficientError(
                                "Hardware memory is insufficient; " + message[2]
                            )
                        if message[1] == "cancelled":
                            raise InterruptedError(message[2])
                        raise HistoryExecutionError(
                            "Worker execution failed; " + message[2]
                        )
                    result = message[1]
                    if message[0] != "result" or result.job_index != identity:
                        raise HistoryExecutionError("Worker result identity mismatch")
                    results[identity] = result
                    publish(len(results), len(jobs))
                    job = next(pending, None)
                    if job is None:
                        connection.send(None)
                        del active[connection]
                    else:
                        check_resources()
                        connection.send(job)
                        active[connection] = (process, job.job_index)
                for connection, (process, _) in active.items():
                    if not process.is_alive() and not connection.poll():
                        raise HistoryExecutionError(
                            f"Worker unexpected exit {process.exitcode}; check hardware/execution environment"
                        )
            return ExecutionBatch(
                tuple(results[i] for i in ids),
                peak,
                launch_available,
                tuple(p.pid for p, _ in children),
                tuple(memory_diagnostics),
            )
        finally:
            for process, connection in children:
                if process.is_alive():
                    process.terminate()
                connection.close()
            for process, _ in children:
                process.join(timeout=2)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=2)
                process.close()
