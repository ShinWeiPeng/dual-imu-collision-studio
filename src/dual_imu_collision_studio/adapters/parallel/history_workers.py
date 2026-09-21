from __future__ import annotations

from dataclasses import dataclass, replace
import multiprocessing
from multiprocessing.connection import Connection
import os
import time
from typing import Any, Callable

import psutil

from dual_imu_collision_studio.domain.learning.model import (
    HardwareMemoryInsufficientError,
    HistoryBatchResult,
    HistoryExecutionError,
    HistoryJob,
    HistoryJobResult,
    HistoryWorkerProgress,
)


HistoryWorker = Callable[[Any, int, Callable[[HistoryWorkerProgress], None]], HistoryJobResult]


def _default_history_worker(
    job: HistoryJob,
    attempt: int,
    progress: Callable[[HistoryWorkerProgress], None],
) -> HistoryJobResult:
    from dual_imu_collision_studio.domain.learning.service import LearningService

    return LearningService().evaluate_history_job(job, attempt=attempt, progress=progress)


def _worker_process_main(
    job: Any,
    attempt: int,
    connection: Connection,
    worker: HistoryWorker,
) -> None:
    started = time.monotonic()

    def emit(value: HistoryWorkerProgress) -> None:
        connection.send(("progress", value))

    try:
        connection.send(("started", os.getpid()))
        result = worker(job, attempt, emit)
        connection.send(("result", result))
    except MemoryError as exc:
        connection.send(("failure", "memory", str(exc) or "MemoryError"))
    except InterruptedError as exc:
        connection.send(("failure", "cancelled", str(exc)))
    except ValueError as exc:
        connection.send(("failure", "data", str(exc)))
    except ArithmeticError as exc:
        connection.send(("failure", "numerical", str(exc)))
    except Exception as exc:
        connection.send(("failure", "product-code", f"{type(exc).__name__}: {exc}"))
    finally:
        try:
            connection.send(("finished", time.monotonic() - started))
        except (BrokenPipeError, EOFError, OSError):
            pass
        connection.close()


@dataclass
class _WorkerAttempt:
    job: Any
    job_index: int
    attempt: int
    process: multiprocessing.Process
    connection: Connection
    started_at: float


class SpawnHistoryExecutor:
    """Run four independent History jobs using the Windows-safe spawn context."""

    def __init__(
        self,
        *,
        worker: HistoryWorker = _default_history_worker,
        maximum_ram_fraction: float = 0.85,
        poll_interval_s: float = 0.01,
    ) -> None:
        if not 0.0 < maximum_ram_fraction <= 1.0:
            raise ValueError("maximum RAM fraction must be between zero and one")
        self._worker = worker
        self._maximum_ram_fraction = maximum_ram_fraction
        self._poll_interval_s = poll_interval_s
        self._context = multiprocessing.get_context("spawn")

    def execute(
        self,
        jobs: tuple[HistoryJob, ...] | tuple[Any, ...],
        progress: Callable[[HistoryWorkerProgress], None] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> HistoryBatchResult:
        if len(jobs) != 4:
            raise ValueError("exactly four requested-History jobs are required")
        publish = progress if progress is not None else lambda _value: None
        is_cancelled = cancelled if cancelled is not None else lambda: False
        launch_available = int(psutil.virtual_memory().available)
        if launch_available <= 0:
            raise HardwareMemoryInsufficientError("Hardware memory availability could not be measured")

        attempts: dict[int, list[float]] = {index: [] for index in range(1, 5)}
        outcomes: dict[int, list[str]] = {index: [] for index in range(1, 5)}
        active: dict[int, _WorkerAttempt] = {}
        results: dict[int, HistoryJobResult] = {}
        worker_pids: list[int] = []
        peak_rss = self._process_tree_rss(())

        def launch(job: Any, job_index: int, attempt: int) -> None:
            parent_connection, child_connection = self._context.Pipe(duplex=False)
            process = self._context.Process(
                target=_worker_process_main,
                args=(job, attempt, child_connection, self._worker),
                name=f"dual-imu-history-{job_index}-attempt-{attempt}",
            )
            started_at = time.monotonic()
            try:
                process.start()
            except Exception as exc:
                duration = time.monotonic() - started_at
                parent_connection.close()
                child_connection.close()
                if process.pid is not None:
                    if process.is_alive():
                        process.terminate()
                    process.join(timeout=1.0)
                attempts[job_index].append(duration)
                outcomes[job_index].append(
                    f"attempt {attempt} startup failure after {duration:.3f}s: "
                    f"{type(exc).__name__}: {exc}"
                )
                if attempt < 2:
                    launch(job, job_index, attempt + 1)
                    return
                raise HistoryExecutionError(
                    f"History worker {job_index} failed to start after one retry; "
                    + "; ".join(outcomes[job_index])
                ) from exc
            child_connection.close()
            if process.pid is not None:
                worker_pids.append(process.pid)
            active[job_index] = _WorkerAttempt(
                job, job_index, attempt, process, parent_connection, started_at
            )

        def stop_all() -> None:
            for item in tuple(active.values()):
                if item.process.is_alive():
                    item.process.terminate()
            for item in tuple(active.values()):
                item.process.join(timeout=2.0)
                item.connection.close()
            active.clear()

        try:
            for job_index, job in enumerate(jobs, start=1):
                launch(job, job_index, 1)

            while active:
                if is_cancelled():
                    stop_all()
                    raise InterruptedError("Learning cancelled")

                rss = self._process_tree_rss(
                    tuple(item.process.pid for item in active.values() if item.process.pid)
                )
                peak_rss = max(peak_rss, rss)
                if rss > launch_available * self._maximum_ram_fraction:
                    stop_all()
                    raise HardwareMemoryInsufficientError(
                        "Hardware memory is insufficient for four History workers"
                    )

                for job_index, item in tuple(active.items()):
                    terminal: tuple[str, Any, Any] | None = None
                    try:
                        while item.connection.poll():
                            message = item.connection.recv()
                            if message[0] == "progress":
                                publish(message[1])
                            elif message[0] in {"result", "failure"}:
                                terminal = message
                    except (EOFError, OSError):
                        pass

                    if terminal is not None:
                        duration = time.monotonic() - item.started_at
                        attempts[job_index].append(duration)
                        item.process.join(timeout=2.0)
                        item.connection.close()
                        active.pop(job_index, None)
                        if terminal[0] == "result":
                            result = terminal[1]
                            results[job_index] = replace(
                                result,
                                job_index=job_index,
                                attempt_durations_s=tuple(attempts[job_index]),
                            )
                            continue
                        failure_kind, message = terminal[1], terminal[2]
                        outcomes[job_index].append(
                            f"attempt {item.attempt} {failure_kind} failure after "
                            f"{duration:.3f}s: {message}"
                        )
                        if failure_kind == "memory":
                            stop_all()
                            raise HardwareMemoryInsufficientError(
                                f"Hardware memory is insufficient for History {job_index}; "
                                + "; ".join(outcomes[job_index])
                            )
                        stop_all()
                        if failure_kind == "cancelled":
                            raise InterruptedError(message or "Learning cancelled")
                        raise HistoryExecutionError(
                            f"History worker {job_index} failed; "
                            + "; ".join(outcomes[job_index])
                        )

                    if not item.process.is_alive():
                        item.process.join(timeout=0.1)
                        duration = time.monotonic() - item.started_at
                        attempts[job_index].append(duration)
                        outcomes[job_index].append(
                            f"attempt {item.attempt} unexpected exit code "
                            f"{item.process.exitcode} after {duration:.3f}s"
                        )
                        item.connection.close()
                        active.pop(job_index, None)
                        if item.attempt < 2:
                            launch(item.job, job_index, item.attempt + 1)
                        else:
                            stop_all()
                            raise HistoryExecutionError(
                                f"History worker {job_index} exited unexpectedly after one retry; "
                                + "; ".join(outcomes[job_index])
                            )

                if active:
                    time.sleep(self._poll_interval_s)
        except BaseException:
            stop_all()
            raise

        ordered = tuple(results[index] for index in range(1, 5))
        return HistoryBatchResult(ordered, peak_rss, launch_available, tuple(worker_pids))

    @staticmethod
    def _process_tree_rss(child_pids: tuple[int, ...]) -> int:
        total = 0
        for pid in (os.getpid(), *child_pids):
            try:
                total += int(psutil.Process(pid).memory_info().rss)
            except (psutil.Error, OSError):
                continue
        return total
