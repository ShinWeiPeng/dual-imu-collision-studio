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
    width = 3 * taps
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
        return 8 * count.feature_rows * (width + 4)

    def build(count):
        evidence_peak = 128 * count.selected_rows + 17 * largest_recording
        # Three append-grown outer lists: features, target views and indexes.
        outer_lists = 3 * (64 + math.ceil(count.feature_rows * 1.125) * pointer)
        object_peak = count.feature_rows * (row_list + scalar * width + view + integer)
        return max(
            evidence_peak,
            56 * count.selected_rows + matrix(count) + object_peak + outer_lists,
        )

    sizes = (width,) + job.point.hidden_layers + (3,)
    parameters = sum(a * b + b for a, b in zip(sizes, sizes[1:]))
    # Weights, gradients, two moments, best/reference/frozen copies and bounded
    # arithmetic temporaries; minibatch activations/deltas and full-loss chunks.
    parameter_workspace = 16 * parameters * 8
    minibatch = 8 * 200 * (4 * sum(sizes) + 2 * width + 12)
    loss_chunk = 8 * 2048 * (sum(sizes) + 9)
    retained_validation = sum(c.common_rows for c in validation) * width * 8
    last_validation = matrix(validation[-1]) + 56 * validation[-1].selected_rows
    retained = matrix(fitting) + retained_validation + last_validation
    construction = max(
        build(fitting),
        matrix(fitting) + retained_validation + max(map(build, validation)),
    )
    normalized_and_scratch = 8 * fitting.feature_rows * (2 * width + 12)
    fit = retained + normalized_and_scratch + max(minibatch, loss_chunk)
    # predict() is full-row: input copies, two hidden activations, output/residual.
    prediction_width = width + 2 * max(sizes) + 18
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
