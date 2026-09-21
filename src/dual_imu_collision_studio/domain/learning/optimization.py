"""Private Learning algorithms; no UI, filesystem or process dependencies."""

from __future__ import annotations

import math
import inspect
from dataclasses import replace
from decimal import Decimal, ROUND_HALF_UP, localcontext
from itertools import product

import numpy as np

from dual_imu_collision_studio.domain.learning.model import (
    CandidateNumericalError,
    ConditionLoss,
    ExecutionBatch,
    FoldJob,
    FoldResult,
    InsufficientTrainingEvidence,
    LearningLogEvidence,
    ParameterPoint,
    ParameterResult,
)


def common_indexes(evidence, maximum_taps):
    segments = np.asarray(evidence.segment_ids)
    if not len(segments):
        return np.empty(0, dtype=np.int64)
    starts = np.maximum.accumulate(
        np.where(
            np.r_[True, segments[1:] != segments[:-1]], np.arange(len(segments)), 0
        )
    )
    return np.flatnonzero(np.arange(len(segments)) - starts >= maximum_taps - 1)


def condition_groups(groups):
    keys = sorted({(g.robot_speed_mm_s, g.collision_offset_mm) for g in groups})
    return tuple(
        (
            key,
            tuple(
                g for g in groups if (g.robot_speed_mm_s, g.collision_offset_mm) == key
            ),
        )
        for key in keys
    )


def check_common_evidence(service, dataset, plan):
    taps = service.maximum_taps(service.validate_dataset(dataset))
    for fold in plan.folds:
        training = tuple(
            g
            for other in plan.folds
            if other.fold_index != fold.fold_index
            for g in other.held_out_groups
        )
        for label, groups in (
            ("Training", training),
            ("Validation", fold.held_out_groups),
        ):
            for key, selected in condition_groups(groups):
                evidence = service._build_group_evidence(dataset, selected)
                if not len(common_indexes(evidence, taps)):
                    raise InsufficientTrainingEvidence(
                        f"Fold {fold.fold_index}, {key}, {label}: no common 128 ms evaluation targets"
                    )


def evaluate_fold_job(service, dataset, job, cancelled=None):
    point = job.point
    maximum_taps = service.maximum_taps(service.validate_dataset(dataset))
    if not 1 <= point.tap_count <= maximum_taps or not 1e-6 <= point.alpha <= 100:
        raise ValueError("Candidate is outside the approved domain")
    if (job.settings.use_robust_refit and not 2 <= point.robust_k <= 32) or (
        not job.settings.use_robust_refit and point.robust_k != 0
    ):
        raise ValueError("Candidate Robust K does not match captured mode")
    try:
        fitting = service._prepare_fir_matrix(
            service._build_group_evidence(dataset, job.training_groups), point.tap_count
        )
        if point.hidden_layers:
            from .mlp import fit

            validation = []
            for _, selected in condition_groups(job.held_out_groups):
                evidence = service._build_group_evidence(dataset, selected)
                indexes = common_indexes(evidence, maximum_taps)
                matrix = service._prepare_fir_matrix(evidence, point.tap_count)
                validation.append(
                    matrix.features[np.searchsorted(matrix.row_indexes, indexes)]
                )
            model = fit(
                fitting.features,
                fitting.targets,
                point.hidden_layers,
                point.alpha,
                point.tap_count,
                job.numeric_type,
                cancelled,
                validation,
            )
        else:
            model = service._fit_mimo_fir_matrix(
                fitting,
                point.tap_count,
                point.alpha,
                "STD",
                point.robust_k,
                "L2_NORM",
                use_robust_refit=job.settings.use_robust_refit,
                numeric_type=job.numeric_type,
            )
        losses = {}
        for subset, groups in ((0, job.training_groups), (1, job.held_out_groups)):
            for key, selected in condition_groups(groups):
                evidence = service._build_group_evidence(dataset, selected)
                indexes = common_indexes(evidence, maximum_taps)
                if not len(indexes):
                    raise InsufficientTrainingEvidence(
                        f"Fold {job.fold_index}, {key}: no common 128 ms evaluation targets"
                    )
                matrix = service._prepare_fir_matrix(evidence, point.tap_count)
                selected_rows = np.searchsorted(matrix.row_indexes, indexes)
                if np.any(
                    selected_rows >= len(matrix.row_indexes)
                ) or not np.array_equal(matrix.row_indexes[selected_rows], indexes):
                    raise ValueError(
                        "Common evaluation targets do not match candidate evidence"
                    )
                if point.hidden_layers:
                    from .mlp import predict

                    prediction = predict(
                        model, matrix.features[selected_rows], job.numeric_type
                    )
                else:
                    prediction = service.target_predict_rows(
                        model.weights,
                        model.biases,
                        matrix.features[selected_rows],
                        job.numeric_type,
                    )
                residual = (
                    np.asarray(
                        matrix.targets[selected_rows],
                        dtype=service._target_dtype(job.numeric_type),
                    )
                    - prediction
                ).astype(np.float64)
                mse = float(np.mean(residual * residual))
                if not math.isfinite(mse):
                    raise CandidateNumericalError("Non-finite MSE")
                losses.setdefault(key, [None, None, 0, 0])[subset] = mse
                losses[key][subset + 2] = len(indexes)
        if any(None in values for values in losses.values()):
            raise ValueError("Training and Validation condition coverage differs")
        conditions = tuple(
            ConditionLoss(*key, *values) for key, values in sorted(losses.items())
        )
        return FoldResult(job.job_index, point, job.fold_index, model, conditions)
    except CandidateNumericalError as exc:
        return FoldResult(
            job.job_index, point, job.fold_index, None, invalid_reason=str(exc)
        )


def rounded_loss(value):
    # Decimal from the shortest round-trippable decimal spelling; never epsilon.
    with localcontext() as context:
        context.prec = 330  # All finite binary64 values plus four fractional digits.
        return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def aggregate_fold_results(point, folds, settings):
    folds = tuple(sorted(folds, key=lambda f: f.fold_index))
    if len(folds) != settings.n_fold or [f.fold_index for f in folds] != list(
        range(1, settings.n_fold + 1)
    ):
        raise ValueError("A parameter requires all N distinct fold results")
    if any(f.point != point for f in folds):
        raise ValueError("Fold parameter identity mismatch")
    if any(f.invalid_reason for f in folds):
        return None
    if any(f.model is None or not f.conditions for f in folds):
        raise ValueError("Unclassified empty fold result")
    keys = [(c.robot_speed_mm_s, c.collision_offset_mm) for c in folds[0].conditions]
    values = []
    for fold in folds:
        if [
            (c.robot_speed_mm_s, c.collision_offset_mm) for c in fold.conditions
        ] != keys:
            raise ValueError("Fold condition coverage mismatch")
        if any(
            not math.isfinite(v) or v < 0
            for c in fold.conditions
            for v in (c.training_mse, c.validation_mse)
        ):
            raise ValueError("Invalid fold MSE")
        values.append([c.loss(settings.include_training_mse) for c in fold.conditions])
    loss = max(
        math.fsum(row[i] / settings.n_fold for row in values) for i in range(len(keys))
    )
    return ParameterResult(point, folds, loss)


def kernel_loss(fold, settings):
    return max(c.loss(settings.include_training_mse) for c in fold.conditions)


def select_fold_kernels(result, settings):
    passing = [
        f
        for f in result.folds
        if all(
            c.validation_mse
            <= c.training_mse * (1 + settings.validation_allowance_percent / 100)
            for c in f.conditions
        )
    ]
    if not passing:
        return ()
    losses = {fold.fold_index: kernel_loss(fold, settings) for fold in passing}
    minimum = min(losses.values())
    return tuple(
        sorted(
            (fold for fold in passing if losses[fold.fold_index] == minimum),
            key=lambda fold: fold.fold_index,
        )
    )


def select_parameter_results(results, settings):
    valid = tuple(result for result in results if result is not None)
    if not valid:
        return ()
    best = min(result.loss for result in valid)
    cutoff = best * (1 + settings.convergence_tolerance_percent / 100)
    return tuple(
        sorted(
            (result for result in valid if result.loss <= cutoff),
            key=lambda result: result.point,
        )
    )


def evaluate_fixed_parameters(
    service, dataset, plan, settings, numeric_type, progress=None, cancelled=None
):
    from dual_imu_collision_studio.domain.learning.model import TrainingMode

    if settings.model_families == ("mlp",):
        from .mlp import evaluate_parameters

        return evaluate_parameters(
            service, dataset, plan, settings, numeric_type, progress, cancelled
        )
    publish = progress or (lambda *_: None)
    stop = cancelled or (lambda: False)
    if settings.training_mode is not TrainingMode.FIXED_GRID:
        raise ValueError("Fixed parameter evaluation requires fixed_grid mode")
    if settings.use_robust_refit:
        raise ValueError("Fixed-grid execution must disable Robust refit")
    candidate_plan = service.build_candidate_plan(
        service.validate_dataset(dataset), settings
    )
    if not candidate_plan.histories or not candidate_plan.ridge_alphas:
        raise ValueError(
            "Fixed-grid Training requires at least one History and Ridge alpha"
        )
    check_common_evidence(service, dataset, plan)
    points = tuple(
        sorted(
            ParameterPoint(history.tap_count, alpha, 0)
            for history, alpha in product(
                candidate_plan.histories, candidate_plan.ridge_alphas
            )
        )
    )
    jobs = []
    for point in points:
        for fold in plan.folds:
            training = tuple(
                group
                for other in plan.folds
                if other.fold_index != fold.fold_index
                for group in other.held_out_groups
            )
            jobs.append(
                FoldJob(
                    len(jobs) + 1,
                    point,
                    fold.fold_index,
                    training,
                    fold.held_out_groups,
                    numeric_type,
                    settings,
                )
            )
    if stop():
        raise InterruptedError("Learning cancelled")
    publish("Fixed-grid CV", 0, len(jobs), None)
    executor = getattr(service, "_learning_executor", None)
    if executor is None:
        outcomes = []
        for job in jobs:
            if stop():
                raise InterruptedError("Learning cancelled")
            outcomes.append(service.evaluate_fold_job(dataset, job))
            publish("Fixed-grid CV", 0, len(jobs) - len(outcomes), None)
        batch = ExecutionBatch(tuple(outcomes))
    else:
        batch = executor.evaluate_folds(
            dataset,
            tuple(jobs),
            lambda done, total: publish("Fixed-grid CV", 0, total - done, None),
            stop,
        )
    expected = {job.job_index: job for job in jobs}
    if len(batch.results) != len(expected) or {
        result.job_index for result in batch.results
    } != set(expected):
        raise ValueError("Incomplete or duplicate fold batch")
    grouped = {point: [] for point in points}
    for result in batch.results:
        job = expected[result.job_index]
        if result.point != job.point or result.fold_index != job.fold_index:
            raise ValueError("Fold job/result identity mismatch")
        grouped[result.point].append(result)
    evaluated = []
    for point in points:
        result = aggregate_fold_results(point, tuple(grouped[point]), settings)
        if result is None:
            publish(
                f"Invalid fixed candidate taps={point.tap_count}, alpha={point.alpha:.17g}: "
                + "; ".join(
                    f"fold {fold.fold_index}: {fold.invalid_reason}"
                    for fold in grouped[point]
                    if fold.invalid_reason
                ),
                len(evaluated),
                0,
                batch,
            )
        else:
            evaluated.append(result)
    if not evaluated:
        return ()
    best = min(result.loss for result in evaluated)
    cutoff = best * (1 + settings.convergence_tolerance_percent / 100)
    winners = select_parameter_results(evaluated, settings)
    winner_points = {result.point for result in winners}
    for index, result in enumerate(sorted(evaluated, key=lambda item: item.point), 1):
        selected = result.point in winner_points
        evidence = LearningLogEvidence(
            "parameter-evaluated",
            result.point,
            result.loss,
            evaluated_count=index,
            pending_count=0,
            disposition="cv-selected" if selected else "cv-rejected",
            reason=(
                f"Within {settings.convergence_tolerance_percent:g}% of minimum raw Parameter Loss"
                if selected
                else f"Raw Parameter Loss exceeds {cutoff:.17g}"
            ),
        )
        publish("Fixed-grid CV", index, 0, batch, evidence)
    return winners


def search_parameters(
    service, dataset, plan, settings, numeric_type, progress=None, cancelled=None
):
    publish = progress or (lambda *_: None)
    stop = cancelled or (lambda: False)
    rate = service.validate_dataset(dataset)
    maximum_taps = service.maximum_taps(rate)
    check_common_evidence(service, dataset, plan)
    cache = {}
    next_job = 0
    best_observed_loss = None

    try:
        progress_parameters = tuple(inspect.signature(publish).parameters.values())
        accepts_evidence = (
            any(
                parameter.kind is inspect.Parameter.VAR_POSITIONAL
                for parameter in progress_parameters
            )
            or sum(
                parameter.kind
                in {
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                }
                for parameter in progress_parameters
            )
            >= 5
        )
    except (TypeError, ValueError):
        accepts_evidence = False

    def publish_evidence(stage, evaluated, pending, batch, evidence):
        if accepts_evidence:
            publish(stage, evaluated, pending, batch, evidence)
        else:
            publish(stage, evaluated, pending, batch)

    def evaluate(points, stage):
        nonlocal next_job, best_observed_loss
        if stop():
            raise InterruptedError("Learning cancelled")
        pending = sorted(set(points) - cache.keys())
        jobs = []
        for point in pending:
            for fold in plan.folds:
                next_job += 1
                training = tuple(
                    g
                    for other in plan.folds
                    if other.fold_index != fold.fold_index
                    for g in other.held_out_groups
                )
                jobs.append(
                    FoldJob(
                        next_job,
                        point,
                        fold.fold_index,
                        training,
                        fold.held_out_groups,
                        numeric_type,
                        settings,
                    )
                )
        if not jobs:
            return
        publish(stage, len(cache), len(jobs), None)
        executor = getattr(service, "_learning_executor", None)
        if executor is None:
            outcomes = []
            for job in jobs:
                if stop():
                    raise InterruptedError("Learning cancelled")
                outcomes.append(service.evaluate_fold_job(dataset, job))
                publish(stage, len(cache), len(jobs) - len(outcomes), None)
            batch = ExecutionBatch(tuple(outcomes))
        else:
            batch = executor.evaluate_folds(
                dataset,
                tuple(jobs),
                lambda done, total: publish(stage, len(cache), total - done, None),
                stop,
            )
        expected = {j.job_index: j for j in jobs}
        if len(batch.results) != len(expected) or {
            r.job_index for r in batch.results
        } != set(expected):
            raise ValueError("Incomplete or duplicate fold batch")
        grouped = {point: [] for point in pending}
        for result in batch.results:
            job = expected[result.job_index]
            if result.point != job.point or result.fold_index != job.fold_index:
                raise ValueError("Fold job/result identity mismatch")
            grouped[result.point].append(result)
        for point in pending:
            result = aggregate_fold_results(point, tuple(grouped[point]), settings)
            cache[point] = result
            if result is None:
                publish(
                    f"Invalid candidate taps={point.tap_count}, alpha={point.alpha:.17g}, K={point.robust_k}: "
                    + "; ".join(
                        f"fold {f.fold_index}: {f.invalid_reason}"
                        for f in grouped[point]
                        if f.invalid_reason
                    ),
                    len(cache),
                    0,
                    batch,
                )
            elif best_observed_loss is None or result.loss < best_observed_loss:
                evidence = LearningLogEvidence(
                    "parameter-best",
                    result.point,
                    result.loss,
                    best_observed_loss,
                    evaluated_count=len(cache),
                    pending_count=0,
                )
                best_observed_loss = result.loss
                publish_evidence(
                    stage,
                    len(cache),
                    0,
                    batch,
                    evidence,
                )
        publish(stage, len(cache), 0, batch)

    coarse = tuple(
        ParameterPoint(
            max(
                1,
                math.floor(h * rate / 1000)
                + (0 if dataset.recordings[0].preprocessing is not None else 1),
            ),
            alpha,
            k,
        )
        for h, alpha, k in product(
            (0, 4, 8, 16, 32, 64, 128),
            service.RIDGE_ALPHAS,
            (2, 4, 8, 16, 24, 32) if settings.use_robust_refit else (0,),
        )
    )
    evaluate(coarse, "Coarse search")
    ranked = sorted(
        (r for r in cache.values() if r is not None), key=lambda r: (r.loss, r.point)
    )
    if not ranked:
        return ()
    cutoff = ranked[min(1, len(ranked) - 1)].loss
    paths = [
        (
            r.point,
            max(1, math.floor(0.032 * rate)),
            4 if settings.use_robust_refit else 1,
            10.0,
        )
        for r in ranked
        if r.loss <= cutoff
    ]
    while paths:
        if stop():
            raise InterruptedError("Learning cancelled")
        neighborhoods = []
        for center, h_step, k_step, ratio in paths:
            points = set()
            for h, alpha, k in product(
                (
                    center.tap_count - h_step,
                    center.tap_count,
                    center.tap_count + h_step,
                ),
                (center.alpha / ratio, center.alpha, center.alpha * ratio),
                (center.robust_k - k_step, center.robust_k, center.robust_k + k_step)
                if settings.use_robust_refit
                else (0,),
            ):
                points.add(
                    ParameterPoint(
                        min(maximum_taps, max(1, h)),
                        min(100.0, max(1e-6, alpha)),
                        min(32, max(2, k)) if settings.use_robust_refit else 0,
                    )
                )
            points.discard(center)
            neighborhoods.append(points)
        evaluate((p for points in neighborhoods for p in points), "Fine search")
        following = []
        for (center, h_step, k_step, ratio), neighbors in zip(
            paths, neighborhoods, strict=True
        ):
            old_loss = cache[center].loss
            valid = [cache[p] for p in neighbors if cache[p] is not None]
            best_loss = min((r.loss for r in valid), default=old_loss)
            final_steps = h_step == 1 and k_step == 1 and ratio == 1.05
            improved = best_loss < old_loss
            material = (
                improved
                and old_loss > 0
                and (old_loss - best_loss) / old_loss
                >= settings.convergence_tolerance_percent / 100
            )
            if improved and (not final_steps or material):
                following.extend(
                    (r.point, h_step, k_step, ratio)
                    for r in sorted(valid, key=lambda r: r.point)
                    if r.loss == best_loss
                )
            elif not final_steps:
                following.append(
                    (
                        center,
                        max(1, h_step // 2),
                        max(1, k_step // 2),
                        max(1.05, math.sqrt(ratio)),
                    )
                )
        paths = following
    return select_parameter_results(cache.values(), settings)


def recording_batch(service, jobs, stop):
    executor = getattr(service, "_learning_executor", None)
    if stop():
        raise InterruptedError("Learning cancelled")
    if executor is not None:
        batch = executor.evaluate_recordings(jobs, stop)
        by_id = {r.job_index: r for r in batch.results}
        if len(batch.results) != len(jobs) or set(by_id) != {j.job_index for j in jobs}:
            raise ValueError("Incomplete recording batch")
        return tuple(by_id[j.job_index] for j in jobs)
    outcomes = []
    for job in jobs:
        if stop():
            raise InterruptedError("Learning cancelled")
        outcomes.append(service.evaluate_recording_job(job))
    return tuple(outcomes)


def qualify_fold(
    service,
    dataset,
    fold,
    evidence,
    state,
    numeric_type,
    stop,
    publish,
    retain_completed,
    qualification_label,
    qualification_evidence,
    completed_count,
    pending_count,
):
    from dual_imu_collision_studio.domain.learning.model import (
        DetectorConfig,
        HistorySpec,
        RecordingJob,
        TrainingMode,
    )

    model = fold.model
    publish(
        "Qualifying",
        0.61,
        qualification_label,
        None,
        evaluated_count=completed_count,
        pending_count=pending_count,
    )
    scores = tuple(
        r.scores
        for r in recording_batch(
            service,
            tuple(
                RecordingJob(i, rec, model, numeric_type)
                for i, rec in enumerate(dataset.recordings)
            ),
            stop,
        )
    )
    publish(
        "Qualifying",
        0.62,
        qualification_label,
        None,
        log_evidence=qualification_evidence,
        evaluated_count=completed_count,
        pending_count=pending_count,
    )
    lower, upper = service._threshold_bounds(
        dataset, scores, state.active_offsets, state.training_speeds
    )
    thresholds = service._threshold_grid(lower, upper, numeric_type)
    if not thresholds:
        return (), f"Empty threshold range: N={lower:.17g}, C={upper:.17g}"
    dtype = service._target_dtype(numeric_type)
    configs = tuple(
        DetectorConfig(
            numeric_type,
            "L2_NORM",
            confirmation,
            float(dtype(threshold)),
            float(dtype(0.5)),
            float(dtype(0.05)),
        )
        for confirmation, threshold in product(service.CONFIRMATION_MODES, thresholds)
    )
    publish(
        "Qualifying",
        0.65,
        f"{qualification_label}: {len(configs)} detector configurations; N={lower:.9g}, C={upper:.9g}",
        None,
        evaluated_count=completed_count,
        pending_count=pending_count,
    )
    candidates = []
    rate = service.validate_dataset(dataset)
    aliases = ()
    if evidence.settings.training_mode is TrainingMode.FIXED_GRID:
        aliases = next(
            (
                item.requested_history_aliases_ms
                for item in service.build_candidate_plan(
                    rate, evidence.settings
                ).histories
                if item.tap_count == model.tap_count
            ),
            (),
        )
    lag_end = (
        model.tap_count
        if getattr(model, "preprocessing", None) is not None
        else model.tap_count - 1
    )
    history = HistorySpec(model.tap_count, aliases, lag_end * 1000 / rate)
    for ci, config in enumerate(configs):
        if stop():
            raise InterruptedError("Learning cancelled")
        jobs = tuple(
            RecordingJob(
                ci * len(dataset.recordings) + ri,
                recording,
                model,
                numeric_type,
                config,
                scores[ri],
            )
            for ri, recording in enumerate(dataset.recordings)
        )
        results = recording_batch(service, jobs, stop)
        metrics = tuple(result.metrics for result in results)
        candidate = service._qualify_model_from_scores(
            dataset,
            model,
            config,
            scores,
            training_speeds=state.training_speeds,
            active_offsets=state.active_offsets,
            candidate_id=f"fold-{fold.fold_index}-{ci}",
            stable_order=ci,
            recording_metrics=metrics,
        )
        completed = replace(
            candidate,
            model=model,
            history=history,
            detector_config=config,
            active_offsets=state.active_offsets,
            excluded_offsets=state.excluded_offsets,
            outer_round=state.outer_round,
            inner_round=state.inner_round,
            cross_validation_fold_count=evidence.settings.n_fold,
            cross_validation_evidence_level="BALANCED_COMPLETE_CYCLE_FOLDS",
            cross_validation_worst_condition_mse=evidence.parameter_loss,
            cross_validation_pooled_mse=math.fsum(
                c.validation_mse
                * (
                    c.validation_sample_count
                    / sum(v.validation_sample_count for v in fold.conditions)
                )
                for c in fold.conditions
            ),
            training_evidence=evidence,
        )
        candidates.append(completed)
        retain_completed(completed)
    # Detector configuration selection is unchanged, independently for each fold kernel.
    return (
        service.select_winner(
            candidates, tuple(sorted({r.robot_speed_mm_s for r in dataset.recordings}))
        ),
    ), ""


def run_learning(
    service, dataset, numeric_type, settings, progress=None, cancelled=None
):
    import random
    import secrets
    import time
    from dual_imu_collision_studio.domain.learning.model import (
        KernelTrainingEvidence,
        LearningCancelled,
        LearningLogEvidence,
        LearningProgress,
        QualificationResult,
        RoundProvenance,
        RunProvenance,
        TrainingMode,
    )

    publish = progress or (lambda *_: None)
    is_cancelled = cancelled or (lambda: False)
    service.validate_dataset(dataset)
    service._target_dtype(numeric_type)
    offsets = tuple(sorted({r.collision_offset_mm for r in dataset.recordings}))
    speeds = tuple(sorted({r.robot_speed_mm_s for r in dataset.recordings}))
    seed = secrets.randbits(64)
    rng = random.Random(seed)
    service.build_cross_validation_plan(
        dataset, offsets, speeds, fold_count=settings.n_fold, seed=seed
    )
    result = QualificationResult((), run_provenance=RunProvenance(seed, settings))

    def stop():
        if is_cancelled():
            qualified = service.rank_qualified_candidates(result.candidates, speeds)
            diagnostic = (
                ()
                if qualified
                else service.rank_diagnostic_candidates(result.candidates)
            )
            retained = qualified if qualified else diagnostic
            raise LearningCancelled(
                replace(
                    result,
                    candidates=retained,
                    diagnostic_candidates=diagnostic,
                )
            )
        return False

    state = service.initial_fallback_state(offsets, speeds)
    while state is not None:
        final_state = state
        round_started = time.monotonic()
        if stop():
            raise InterruptedError("Learning cancelled")

        def emit(
            stage,
            fraction,
            message,
            batch=None,
            log_evidence=None,
            evaluated_count=None,
            pending_count=None,
        ):
            publish(
                LearningProgress(
                    stage,
                    fraction,
                    state.outer_round,
                    state.inner_round,
                    message,
                    state.active_offsets,
                    state.excluded_offsets,
                    state.training_speeds,
                    offsets,
                    speeds,
                    process_tree_peak_rss_bytes=batch.peak_rss_bytes if batch else 0,
                    launch_available_ram_bytes=batch.launch_available_ram_bytes
                    if batch
                    else 0,
                    worker_pids=batch.worker_pids if batch else (),
                    round_elapsed_s=time.monotonic() - round_started,
                    log_evidence=log_evidence,
                    evaluated_count=evaluated_count,
                    pending_count=pending_count,
                )
            )

        emit(
            "Learning",
            0.05,
            "Checking round evidence and allocating complete Cycle folds",
        )
        missing = service._missing_search_evidence(
            dataset, state.active_offsets, state.training_speeds
        )
        round_candidates = []
        reason = missing
        if not missing:
            round_seed = rng.getrandbits(64)
            plan = service.build_cross_validation_plan(
                dataset,
                state.active_offsets,
                state.training_speeds,
                fold_count=settings.n_fold,
                seed=round_seed,
            )
            provenance = RoundProvenance(
                state.outer_round,
                state.inner_round,
                round_seed,
                state.active_offsets,
                state.training_speeds,
                plan,
            )
            result = replace(
                result,
                run_provenance=replace(
                    result.run_provenance,
                    rounds=result.run_provenance.rounds + (provenance,),
                ),
            )
            try:
                evaluate = (
                    service.evaluate_fixed_parameters
                    if settings.training_mode is TrainingMode.FIXED_GRID
                    else service.search_parameters
                )
                parameters = evaluate(
                    dataset,
                    plan,
                    settings,
                    numeric_type,
                    lambda stage, count, pending, batch, evidence=None: emit(
                        "Learning",
                        0.3,
                        f"{stage}: {count} parameter configurations evaluated; {pending} fold jobs pending",
                        batch,
                        evidence,
                        count,
                        pending,
                    ),
                    stop,
                )
            except InsufficientTrainingEvidence as exc:
                parameters = ()
                reason = str(exc)
            if not parameters and not reason:
                reason = "No numerically valid parameter configurations"
            if parameters:
                final = parameters[0]
                emit(
                    "Learning",
                    0.6,
                    f"Round final Parameter Loss {rounded_loss(final.loss)}",
                    log_evidence=LearningLogEvidence(
                        "parameter-final",
                        final.point,
                        float(rounded_loss(final.loss)),
                    ),
                )
            admitted = tuple(
                (parameter, fold)
                for parameter in parameters
                for fold in service.select_fold_kernels(parameter, settings)
            )
            survivor_count = len(admitted)
            for admitted_index, (parameter, fold) in enumerate(admitted, 1):
                completed_count = admitted_index - 1
                pending_count = survivor_count - completed_count
                selected_kernel_loss = kernel_loss(fold, settings)
                validation_outcomes = tuple(
                    (
                        condition.robot_speed_mm_s,
                        condition.collision_offset_mm,
                        condition.validation_mse
                        <= condition.training_mse
                        * (1 + settings.validation_allowance_percent / 100),
                    )
                    for condition in fold.conditions
                )
                admission_log_evidence = LearningLogEvidence(
                    "kernel-admitted",
                    parameter.point,
                    parameter_loss=parameter.loss,
                    fold_index=fold.fold_index,
                    kernel_loss=selected_kernel_loss,
                    validation_pass=all(item[2] for item in validation_outcomes),
                    validation_outcomes=validation_outcomes,
                    evaluated_count=completed_count,
                    pending_count=pending_count,
                )
                evidence = KernelTrainingEvidence(
                    settings,
                    fold.fold_index,
                    fold.conditions,
                    parameter.loss,
                    selected_kernel_loss,
                    round_seed,
                    plan,
                )
                committed_before_fold = len(result.candidates)

                def retain_completed(candidate):
                    nonlocal result
                    completed = replace(
                        candidate,
                        candidate_id=f"k{len(result.candidates) + 1:03d}",
                    )
                    result = service.retain_round_winner(result, completed)

                selected, bound_reason = qualify_fold(
                    service,
                    dataset,
                    fold,
                    evidence,
                    state,
                    numeric_type,
                    stop,
                    emit,
                    retain_completed,
                    f"Qualification {admitted_index}/{survivor_count}: "
                    f"taps={parameter.point.tap_count}, alpha={parameter.point.alpha:.17g}, "
                    f"K={parameter.point.robust_k}, Fold {fold.fold_index}",
                    admission_log_evidence,
                    completed_count,
                    pending_count,
                )
                result = replace(
                    result,
                    candidates=result.candidates[:committed_before_fold],
                )
                for candidate in selected:
                    committed = replace(
                        candidate,
                        candidate_id=f"k{len(result.candidates) + 1:03d}",
                    )
                    round_candidates.append(committed)
                    result = service.retain_round_winner(result, committed)
                if bound_reason:
                    reason = bound_reason
                emit(
                    "Qualifying",
                    0.65,
                    f"Qualification {admitted_index}/{survivor_count} completed: "
                    f"taps={parameter.point.tap_count}, alpha={parameter.point.alpha:.17g}, "
                    f"K={parameter.point.robust_k}, Fold {fold.fold_index}",
                    evaluated_count=admitted_index,
                    pending_count=survivor_count - admitted_index,
                )
            if parameters and not survivor_count:
                reason = "Validation failed: no passing fold kernels in the best parameter configurations"
        matches = any(service.round_can_stop(c) for c in round_candidates)
        if not round_candidates:
            skipped = LearningProgress(
                "Refining Speed Range",
                0.9,
                state.outer_round,
                state.inner_round,
                reason,
                state.active_offsets,
                state.excluded_offsets,
                state.training_speeds,
                offsets,
                speeds,
                unavailable_reason=reason,
            )
            result = replace(
                result, unavailable_rounds=result.unavailable_rounds + (skipped,)
            )
            publish(skipped)
        next_state = service._next_fallback_state(state, speeds, range_matches=matches)
        if round_candidates:
            if next_state is None:
                fallback_reason = (
                    "Retained evaluated kernels; no active Collision Offset remains"
                )
            elif next_state.outer_round == state.outer_round:
                fallback_reason = (
                    "Qualified range did not match the Training range; reducing Training speeds to "
                    + ", ".join(
                        f"{speed:g} mm/s" for speed in next_state.training_speeds
                    )
                )
            else:
                newly_excluded = tuple(
                    offset
                    for offset in next_state.excluded_offsets
                    if offset not in state.excluded_offsets
                )
                fallback_reason = (
                    "Completed the current speed scope; excluding Collision Offset "
                    + ", ".join(f"{offset:g} mm" for offset in newly_excluded)
                )
            emit("Refining Speed Range", 0.9, fallback_reason)
        state = next_state
    publish(
        LearningProgress(
            "Complete",
            1.0,
            final_state.outer_round,
            final_state.inner_round,
            "Learning and Qualification completed.",
        )
    )
    return replace(
        result,
        diagnostic_candidates=service.rank_diagnostic_candidates(result.candidates),
    )
