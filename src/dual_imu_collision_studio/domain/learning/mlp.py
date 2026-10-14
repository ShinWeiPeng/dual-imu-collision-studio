"""Private NumPy MLP algorithms; immutable models cross the Learning boundary."""

from dataclasses import replace
import numpy as np

from dual_imu_collision_studio.domain.learning.model import (
    CandidateNumericalError,
    FrozenMlpModel,
)


def _forward(weights, biases, x):
    values = [x]
    for i, (w, b) in enumerate(zip(weights, biases)):
        z = values[-1] @ w + b
        values.append(np.maximum(z, 0) if i < len(weights) - 1 else z)
    return values


def predict(model, features, numeric_type):
    dtype = np.dtype(numeric_type)
    x = np.asarray(features, dtype=dtype)
    for i, (w, b) in enumerate(zip(model.weights, model.biases)):
        # Fixed reduction order regardless of batch size or BLAS implementation.
        x = np.einsum("ni,ij->nj", x, w.astype(dtype, copy=False), optimize=False) + b
        if i < len(model.weights) - 1:
            np.maximum(x, 0, out=x)
    if not np.all(np.isfinite(x)):
        raise CandidateNumericalError("Non-finite MLP prediction")
    return x


def objective_gradient(weights, biases, x, y, alpha):
    values = _forward(weights, biases, x)
    error = values[-1] - y
    loss = float(
        np.mean(np.sum(error * error, axis=1))
        + alpha * sum(np.sum(w * w) for w in weights)
    )
    delta = 2 * error / len(x)
    gw, gb = [], []
    for i in range(len(weights) - 1, -1, -1):
        gw.append(values[i].T @ delta + 2 * alpha * weights[i])
        gb.append(delta.sum(axis=0))
        if i:
            delta = (delta @ weights[i].T) * (values[i] > 0)
    return loss, list(reversed(gw)), list(reversed(gb))


def fit(
    features,
    targets,
    hidden,
    alpha,
    taps,
    numeric_type,
    cancelled=None,
    validation_features=(),
):
    stop = cancelled or (lambda: False)
    x, y = np.asarray(features, dtype=np.float64), np.asarray(targets, dtype=np.float64)
    if not len(x) or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("MLP requires finite nonempty training data")
    mean, scale, center = x.mean(axis=0), x.std(axis=0), y.mean(axis=0)
    degenerate = scale <= 64 * np.finfo(float).eps * np.maximum(
        1, np.max(np.abs(x), axis=0)
    )
    scale[degenerate] = 1
    target_scale = y.std(axis=0)
    target_scale[
        target_scale
        <= 64 * np.finfo(float).eps * np.maximum(1, np.max(np.abs(y), axis=0))
    ] = 1
    x, y = (x - mean) / scale, (y - center) / target_scale
    x[:, degenerate] = 0
    rng = np.random.default_rng(42)
    sizes = (x.shape[1],) + tuple(hidden) + (y.shape[1],)
    weights, biases = [], []
    for a, b in zip(sizes, sizes[1:]):
        limit = np.sqrt(6 / (a + b))
        weights.append(rng.uniform(-limit, limit, (a, b)))
        biases.append(rng.uniform(-limit, limit, b))
    params = weights + biases
    moments = [np.zeros_like(p) for p in params]
    squares = [np.zeros_like(p) for p in params]
    best_loss, anchor, stale, step = float("inf"), None, 0, 0
    reason = "epoch-cap"
    for epoch in range(1, 201):
        order = rng.permutation(len(x))
        for start in range(0, len(x), 200):
            if stop():
                raise InterruptedError("Learning cancelled")
            indexes = order[start : start + 200]
            _, gw, gb = objective_gradient(
                weights, biases, x[indexes], y[indexes], alpha
            )
            step += 1
            for p, g, m, v in zip(params, gw + gb, moments, squares):
                m *= 0.9
                m += 0.1 * g
                v *= 0.999
                v += 0.001 * g * g
                p -= (
                    0.001
                    * (m / (1 - 0.9**step))
                    / (np.sqrt(v / (1 - 0.999**step)) + 1e-8)
                )
        # Forward-only complete loss, with one L2 term and bounded chunks.
        squared = 0.0
        for start in range(0, len(x), 2048):
            if stop():
                raise InterruptedError("Learning cancelled")
            e = (
                _forward(weights, biases, x[start : start + 2048])[-1]
                - y[start : start + 2048]
            )
            squared += float(np.sum(e * e))
        loss = squared / len(x) + alpha * sum(float(np.sum(w * w)) for w in weights)
        if not np.isfinite(loss):
            raise CandidateNumericalError("Non-finite MLP objective")
        if loss < best_loss:
            best_loss, best = loss, [p.copy() for p in params]
        if anchor is None or loss < anchor * (1 - 0.0001):
            anchor, stale = loss, 0
        else:
            stale += 1
        if loss == 0 or stale >= 20:
            reason = "zero-loss" if loss == 0 else "patience"
            break
    count = len(weights)
    weights, biases = best[:count], best[count:]
    weights[-1] *= target_scale
    biases[-1] *= target_scale
    weights[0][degenerate] = 0
    reference_w, reference_b = [w.copy() for w in weights], [b.copy() for b in biases]
    weights[0] /= scale[:, None]
    biases[0] -= mean @ weights[0]
    biases[-1] += center
    dtype = np.dtype(numeric_type)
    with np.errstate(over="ignore", invalid="ignore"):
        frozen_weights = tuple(w.astype(dtype) for w in weights)
        frozen_biases = tuple(b.astype(dtype) for b in biases)
    if any(
        not np.all(np.isfinite(value)) for value in (*frozen_weights, *frozen_biases)
    ):
        raise CandidateNumericalError("MLP parameters overflow selected numeric type")
    model = FrozenMlpModel(
        taps,
        frozen_weights,
        frozen_biases,
        alpha,
        np.zeros(y.shape[1], dtype=dtype),
        np.ones(y.shape[1], dtype=dtype),
        len(x),
        len(x),
        epoch,
        reason,
    )
    for values in (features, *validation_features):
        for start in range(0, len(values), 2048):
            if stop():
                raise InterruptedError("Learning cancelled")
            validate_folded(
                model,
                reference_w,
                reference_b,
                mean,
                scale,
                center,
                values[start : start + 2048],
            )
    residual = (
        np.asarray(targets, dtype=dtype) - predict(model, features, numeric_type)
    ).astype(np.float64)
    centers = residual.mean(axis=0)
    scales = np.sqrt(np.mean((residual - centers) ** 2, axis=0))
    limit = 64 * np.finfo(float).eps * np.maximum(1, np.max(np.abs(residual), axis=0))
    scales = np.where(scales <= limit, 1.0, scales)
    with np.errstate(over="ignore", invalid="ignore", under="ignore"):
        centers, scales = centers.astype(dtype), scales.astype(dtype)
    if (
        not np.all(np.isfinite(centers))
        or not np.all(np.isfinite(scales))
        or np.any(scales <= 0)
    ):
        raise CandidateNumericalError(
            "MLP residual normalization is invalid in selected numeric type"
        )
    return replace(model, residual_centers=centers, residual_scales=scales)


def validate_folded(model, weights, biases, mean, scale, center, features):
    """Check explicit preprocessing against frozen inference with propagated bounds.

    Bounds account for coefficient/input casts, dot accumulation, folding and
    bias rounding; ReLU is 1-Lipschitz. They are not fitted to observed errors.
    """
    raw = np.asarray(features, dtype=np.float64)
    if not len(raw):
        return
    expected = _forward(weights, biases, (raw - mean) / scale)[-1] + center
    dtype = model.weights[0].dtype
    eps = np.finfo(dtype).eps
    eps64 = np.finfo(np.float64).eps
    x = raw.astype(dtype).astype(np.float64)
    bound = np.abs(x - raw)
    reference = raw
    for i, (w, b) in enumerate(zip(weights, biases)):
        ideal_w, ideal_b = w, b
        folding = np.zeros_like(b)
        if i == 0:
            ideal_w = w / scale[:, None]
            ideal_b = b - mean @ ideal_w
            folding = (
                (len(mean) + 8) * eps64 * (np.abs(mean) @ np.abs(ideal_w) + np.abs(b))
            )
            folding = folding + 8 * eps64 * (np.abs(raw) @ np.abs(ideal_w))
        if i == len(weights) - 1:
            ideal_b = ideal_b + center
            folding = folding + 4 * eps64 * (np.abs(b) + np.abs(center))
        frozen_w, frozen_b = (
            model.weights[i].astype(np.float64),
            model.biases[i].astype(np.float64),
        )
        gamma = (ideal_w.shape[0] + 2) * eps
        if gamma >= 0.5:
            raise CandidateNumericalError("MLP accumulation bound is not informative")
        gamma /= 1 - gamma
        # Use the expected cast, so corrupted frozen values cannot inflate their
        # own allowed error. Parameter mismatch is a transform defect.
        cast_w, cast_b = (
            ideal_w.astype(dtype).astype(np.float64),
            ideal_b.astype(dtype).astype(np.float64),
        )
        if not np.array_equal(frozen_w, cast_w) or not np.array_equal(frozen_b, cast_b):
            raise CandidateNumericalError("MLP folding parameter mismatch")
        bound = (
            bound @ np.abs(cast_w)
            + np.abs(reference) @ np.abs(ideal_w - cast_w)
            + np.abs(ideal_b - cast_b)
            + folding
            + gamma * ((np.abs(reference) + bound) @ np.abs(cast_w) + np.abs(cast_b))
        )
        reference = reference @ ideal_w + ideal_b
        if i < len(weights) - 1:
            reference = np.maximum(reference, 0)
    actual = predict(model, raw, dtype).astype(np.float64)
    if not np.all(np.isfinite(bound)) or np.any(
        np.abs(actual - expected) > bound + np.finfo(dtype).tiny
    ):
        raise CandidateNumericalError(
            "MLP explicit/folded prediction exceeds numerical error bound"
        )


def replay_arrays(recording, model, numeric_type):
    dtype = np.dtype(numeric_type)
    internal = np.asarray(recording.internal_imu, dtype=dtype)
    resets = np.array(recording.discontinuity_before, dtype=bool, copy=True)
    if len(resets):
        resets[0] = True
    history = np.zeros((internal.shape[1], model.tap_count), dtype=dtype)
    prediction = np.empty_like(internal)
    for row in range(len(internal)):
        if resets[row]:
            history.fill(0)
        history[:, 1:] = history[:, :-1]
        history[:, 0] = internal[row]
        prediction[row] = predict(model, history.reshape(1, -1), numeric_type)[0]
    residual = np.asarray(recording.external_imu, dtype=dtype) - prediction
    normalized = (residual - model.residual_centers) / model.residual_scales
    if not np.all(np.isfinite(normalized)):
        raise CandidateNumericalError("Non-finite MLP normalized residual")
    return prediction, residual, normalized, resets


def evaluate_parameters(
    service, dataset, plan, settings, numeric_type, progress=None, cancelled=None
):
    from itertools import product
    from . import optimization
    from dual_imu_collision_studio.domain.learning.model import (
        FoldJob,
        ParameterPoint,
        LearningLogEvidence,
    )

    publish, stop = progress or (lambda *_: None), cancelled or (lambda: False)
    if not settings.selections_ready:
        raise ValueError("MLP requires History, L2 and widths for every hidden layer")
    optimization.check_common_evidence(service, dataset, plan)
    histories = service.build_candidate_plan(
        service.validate_dataset(dataset), settings
    ).histories
    # Enumerate lazily and keep only candidates still within the monotonically
    # decreasing minimum-loss cutoff. No giant Cartesian job list is allocated.
    retained, best, index = [], float("inf"), 0
    evaluated = []
    executor = getattr(service, "_learning_executor", None)
    for widths in product(*settings.mlp_layer_widths):
        for history, alpha in product(histories, settings.mlp_l2):
            if stop():
                raise InterruptedError("Learning cancelled")
            point = ParameterPoint(history.tap_count, alpha, 0, tuple(widths))
            jobs = tuple(
                FoldJob(
                    index * plan.fold_count + f.fold_index,
                    point,
                    f.fold_index,
                    tuple(
                        g
                        for other in plan.folds
                        if other.fold_index != f.fold_index
                        for g in other.held_out_groups
                    ),
                    f.held_out_groups,
                    numeric_type,
                    settings,
                )
                for f in plan.folds
            )
            if executor:
                batch = executor.evaluate_folds(dataset, jobs, None, stop)
                if batch.memory_diagnostics:
                    publish(
                        "MLP memory: " + " | ".join(batch.memory_diagnostics),
                        index,
                        0,
                        batch,
                    )
                folds = batch.results
            else:
                batch = None
                folds = tuple(
                    optimization.evaluate_fold_job(service, dataset, j, stop)
                    for j in jobs
                )
            if len(folds) != len(jobs) or {f.job_index for f in folds} != {
                j.job_index for j in jobs
            }:
                raise ValueError("MLP fold job identity mismatch")
            by_id = {j.job_index: j for j in jobs}
            if any(
                f.point != by_id[f.job_index].point
                or f.fold_index != by_id[f.job_index].fold_index
                for f in folds
            ):
                raise ValueError("MLP fold result does not match dispatched job")
            result = optimization.aggregate_fold_results(point, folds, settings)
            index += 1
            if result is not None:
                best = min(best, result.loss)
                cutoff = best * (1 + settings.convergence_tolerance_percent / 100)
                retained = [r for r in retained if r.loss <= cutoff]
                if result.loss <= cutoff:
                    retained.append(result)
            if result is not None:
                evaluated.append((point, result.loss))
            if result is None:
                publish(
                    f"Invalid MLP taps={point.tap_count}, L2={alpha:g}, hidden={widths}: "
                    + "; ".join(
                        f"fold {f.fold_index}: {f.invalid_reason}"
                        for f in folds
                        if f.invalid_reason
                    ),
                    index,
                    0,
                    batch,
                )
            else:
                publish("MLP grid " + str(widths), index, 0, batch)
    winners = {r.point for r in retained}
    for count, (point, loss) in enumerate(evaluated, 1):
        selected = point in winners
        evidence = LearningLogEvidence(
            "parameter-evaluated",
            point,
            parameter_loss=loss,
            evaluated_count=count,
            disposition="cv-selected" if selected else "cv-rejected",
            reason="Within family minimum Loss tolerance"
            if selected
            else "Exceeds family minimum Loss tolerance",
        )
        publish("MLP grid " + str(point.hidden_layers), count, 0, None, evidence)
    return tuple(sorted(retained, key=lambda r: r.point))


def run_families(
    service, dataset, numeric_type, settings, progress=None, cancelled=None
):
    from .optimization import run_learning
    from dual_imu_collision_studio.domain.learning.model import (
        QualificationResult,
        LearningCancelled,
        TrainingMode,
    )

    if settings.model_families == ("fir",):
        return run_learning(
            service, dataset, numeric_type, settings, progress, cancelled
        )
    if not settings.selections_ready:
        raise ValueError("Select models and all required model parameters")
    results, runs, diagnostics, unavailable = [], [], [], []

    def merge(result, family):
        mapped = {
            c.candidate_id: replace(c, candidate_id=family + "-" + c.candidate_id)
            for c in result.candidates
        }
        results.extend(mapped.values())
        diagnostics.extend(
            mapped.get(
                c.candidate_id, replace(c, candidate_id=family + "-" + c.candidate_id)
            )
            for c in result.diagnostic_candidates
        )
        unavailable.extend(
            replace(event, message=family.upper() + ": " + event.message)
            for event in result.unavailable_rounds
        )
        if result.run_provenance:
            runs.append(replace(result.run_provenance, family=family))

    def combined():
        return QualificationResult(
            tuple(results),
            tuple(diagnostics),
            tuple(unavailable),
            runs[0] if runs else None,
            tuple(runs),
        )

    for family_index, family in enumerate(settings.model_families):
        captured = replace(settings, model_families=(family,))
        if family == "mlp":
            captured = replace(
                captured, training_mode=TrainingMode.FIXED_GRID, use_robust_refit=False
            )

        def report(event):
            if progress:
                stage = (
                    "Learning"
                    if event.stage == "Complete"
                    and family_index < len(settings.model_families) - 1
                    else event.stage
                )
                progress(
                    replace(
                        event,
                        stage=stage,
                        fraction=(family_index + event.fraction)
                        / len(settings.model_families),
                        message=family.upper() + ": " + event.message,
                    )
                )

        try:
            result = run_learning(
                service, dataset, numeric_type, captured.for_run(), report, cancelled
            )
        except LearningCancelled as exc:
            merge(exc.result, family)
            raise LearningCancelled(combined()) from exc
        merge(result, family)
    return combined()
