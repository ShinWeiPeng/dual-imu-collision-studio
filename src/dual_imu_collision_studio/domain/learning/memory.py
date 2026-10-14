"""Fold allocation accounting; no feature matrix or model is built for admission."""

from dataclasses import dataclass

import math

import struct

import sys


import numpy as np


from dual_imu_collision_studio.domain.learning.service import LearningService


@dataclass(frozen=True, slots=True)
class EvidenceRowCounts:
    selected_rows: int

    feature_rows: int

    common_rows: int


@dataclass(frozen=True, slots=True)
class FoldMemoryEstimate:
    job_index: int

    training_rows: int

    validation_rows: int

    dataset_bytes: int

    components: tuple[tuple[str, int], ...]

    peak_bytes: int


def count_evidence_rows(dataset, groups, taps, maximum_taps):

    # Reuse the authoritative interval/segment construction. Its compact XYZ

    # evidence is released here; History-expanded features are never allocated.

    evidence = LearningService._build_group_evidence(dataset, groups)

    size = len(evidence.segment_ids)

    if not size:
        return EvidenceRowCounts(0, 0, 0)

    indexes = np.arange(size)

    starts = np.maximum.accumulate(
        np.where(np.r_[True, np.diff(evidence.segment_ids) != 0], indexes, 0)
    )

    finite = np.all(np.isfinite(evidence.internal_imu), axis=1)

    prefix = np.r_[0, np.cumsum(~finite)]

    first = np.maximum(0, indexes - taps + 1)

    valid = (
        (indexes - starts >= taps - 1)
        & (prefix[indexes + 1] == prefix[first])
        & np.all(np.isfinite(evidence.external_imu), axis=1)
    )

    return EvidenceRowCounts(
        size,
        int(np.count_nonzero(valid)),
        int(np.count_nonzero(valid & (indexes - starts >= maximum_taps - 1))),
    )


def estimate_fold_memory(dataset, job):

    from .optimization import condition_groups

    taps = job.point.tap_count

    channels = dataset.recordings[0].internal_imu.shape[1]

    width = channels * taps

    maximum_taps = math.floor(0.128 * LearningService().validate_dataset(dataset)) + 1

    fitting = count_evidence_rows(dataset, job.training_groups, taps, maximum_taps)

    training = tuple(
        count_evidence_rows(dataset, groups, taps, maximum_taps)
        for _, groups in condition_groups(job.training_groups)
    )

    validation = tuple(
        count_evidence_rows(dataset, groups, taps, maximum_taps)
        for _, groups in condition_groups(job.held_out_groups)
    )

    dataset_bytes = sum(
        sum(
            values.nbytes + sys.getsizeof(values) - values.nbytes
            if values.flags.owndata
            else values.nbytes + sys.getsizeof(values)
            for values in (
                r.time_s,
                r.internal_imu,
                r.external_imu,
                r.discontinuity_before,
            )
        )
        + sys.getsizeof(r)
        + sys.getsizeof(r.intervals)
        + sum(sys.getsizeof(i) for i in r.intervals)
        for r in dataset.recordings
    )

    # CPython list growth and NumPy scalar/view objects in _fir_rows coexist

    # with the final dense arrays until its return. Measure fixed-size objects

    # on this interpreter and round each to its 16-byte allocator size class.

    align = lambda n: (n + 15) // 16 * 16

    scalar = align(sys.getsizeof(np.float64(0)))

    row_list = align(sys.getsizeof([0 for _ in range(width)]))

    view = align(sys.getsizeof(np.empty((0, 3))[0:0]))

    integer = align(sys.getsizeof(0))

    pointer = struct.calcsize("P")

    largest_recording = max(len(r.time_s) for r in dataset.recordings)

    def matrix(count):

        return 8 * count.feature_rows * (width + channels + 1)

    def build(count):

        evidence_peak = (
            32 * channels + 32
        ) * count.selected_rows + 17 * largest_recording

        # Three append-grown outer lists: features, target views and indexes.

        outer_lists = 3 * (64 + math.ceil(count.feature_rows * 1.125) * pointer)

        object_peak = count.feature_rows * (row_list + scalar * width + view + integer)

        return max(
            evidence_peak,
            (16 * channels + 8) * count.selected_rows
            + matrix(count)
            + object_peak
            + outer_lists,
        )

    if not job.point.hidden_layers:
        # FIR owns a different allocation model from the MLP optimizer below.
        # Full serialized recordings (including optional eligibility masks) live
        # for the worker lifetime, even when a fold selects only some intervals.
        dataset_bytes += sum(
            mask.nbytes + sys.getsizeof(mask)
            for r in dataset.recordings
            if (mask := getattr(r, "training_eligible", None)) is not None
        )
        conditions = (*training, *validation)
        largest_matrix = max((matrix(c) for c in conditions), default=0)
        largest_evidence = max(
            ((16 * channels + 8) * c.selected_rows for c in conditions), default=0
        )
        # evaluate_fold_job retains the fitting matrix. On reassignment of its
        # condition matrix, the preceding matrix/prediction/index arrays remain
        # alive until the RHS finishes. Charge those alongside the next build.
        condition_rows = max((c.feature_rows for c in conditions), default=0)
        condition_scratch = 8 * condition_rows * (2 * width + 10 * channels + 4)
        construction = max(
            build(fitting),
            matrix(fitting)
            + largest_matrix
            + largest_evidence
            + condition_scratch
            + max((build(c) for c in conditions), default=0),
        )
        rows = fitting.feature_rows
        # _ridge_source_scale: centering/standardization and abs/std scratch;
        # Gram assembly, regularizer, solve copies and right-hand-side work.
        ridge = 8 * rows * (2 * width + 3 * channels) + 8 * (
            5 * width * width + 6 * width * channels + 8 * width + 4 * channels
        )
        # Optional robust refit retains residuals/scores/masks, Python sorted
        # indexes and seed sets, while copied selected features enter Ridge.
        robust = 0
        if job.settings.use_robust_refit:
            robust = 8 * rows * (width + 9 * channels + 6) + rows * (
                4 * integer + 12 * pointer + 4
            )
        # Calibration can overlap selected float64 features, a target-precision
        # input copy, predictions and median/MAD residual temporaries. Using
        # eight bytes for either target precision is conservative.
        calibration = 8 * rows * (2 * width + 10 * channels + 4)
        fit = matrix(fitting) + max(ridge + robust, calibration + robust)
        scoring = (
            matrix(fitting) + largest_matrix + largest_evidence + condition_scratch
        )
        # Mutable/frozen/target-cast weights, bias and scale metadata, plus the
        # bounded per-job result retained by the parent while later jobs finish.
        parameter_workspace = 8 * (8 * (width * channels + 5 * channels))
        components = (
            ("matrix_construction", int(construction)),
            ("fit", int(fit)),
            ("scoring", int(scoring)),
            ("parameters", int(parameter_workspace)),
        )
        return FoldMemoryEstimate(
            job.job_index,
            fitting.feature_rows,
            sum(c.common_rows for c in validation),
            int(dataset_bytes),
            components,
            int(dataset_bytes + max(construction, fit, scoring) + parameter_workspace),
        )

    sizes = (width,) + job.point.hidden_layers + (channels,)

    parameters = sum(a * b + b for a, b in zip(sizes, sizes[1:]))

    # Weights, gradients, two moments, best/reference/frozen copies and bounded

    # arithmetic temporaries; minibatch activations/deltas and full-loss chunks.

    parameter_workspace = 16 * parameters * 8

    minibatch = 8 * 200 * (4 * sum(sizes) + 2 * width + 4 * channels)

    loss_chunk = 8 * 2048 * (sum(sizes) + 3 * channels)

    retained_validation = sum(c.common_rows for c in validation) * width * 8

    last_validation = (
        matrix(validation[-1]) + (16 * channels + 8) * validation[-1].selected_rows
    )

    retained = matrix(fitting) + retained_validation + last_validation

    construction = max(
        build(fitting),
        matrix(fitting) + retained_validation + max(map(build, validation)),
    )

    normalized_and_scratch = 8 * fitting.feature_rows * (2 * width + 4 * channels)

    fit = retained + normalized_and_scratch + max(minibatch, loss_chunk)

    # predict() is full-row: input copies, two hidden activations, output/residual.

    prediction_width = width + 2 * max(sizes) + 6 * channels

    prediction = (
        8
        * max(fitting.feature_rows, *(c.common_rows for c in (*training, *validation)))
        * prediction_width
    )

    scoring = retained + max(map(build, (*training, *validation))) + prediction

    components = (
        ("matrix_construction", int(construction)),
        ("fit", int(fit)),
        ("scoring", int(scoring)),
        ("parameters", int(parameter_workspace)),
    )

    return FoldMemoryEstimate(
        job.job_index,
        fitting.feature_rows,
        sum(c.common_rows for c in validation),
        int(dataset_bytes),
        components,
        int(dataset_bytes + max(construction, fit, scoring) + parameter_workspace),
    )
