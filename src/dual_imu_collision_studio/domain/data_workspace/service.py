from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
import math

import numpy as np

from dual_imu_collision_studio.domain.data_workspace.model import (
    ActivityKind,
    AnnotationInterval,
    AnnotationTemplate,
    AnnotationTemplateEvent,
    Recording,
    WaveformViewportProjection,
)


class WorkspaceService:
    """Validates explicit interval truth and derives Normal Robot Motion."""

    _EVENT_KINDS = frozenset(
        {ActivityKind.PICK, ActivityKind.PUT, ActivityKind.FORK_COLLISION, ActivityKind.IGNORE}
    )
    _POSITIVE_EVENT_KINDS = frozenset(
        {ActivityKind.PICK, ActivityKind.PUT, ActivityKind.FORK_COLLISION}
    )

    def project_waveform_viewport(
        self,
        values: object,
        viewport_start: float,
        viewport_end: float,
        plot_width: int,
    ) -> WaveformViewportProjection:
        """Project original three-axis samples without losing visible extrema."""
        width = int(plot_width)
        if width < 1:
            raise ValueError("waveform plot width must be positive")
        raw_start = float(viewport_start)
        raw_end = float(viewport_end)
        if not math.isfinite(raw_start) or not math.isfinite(raw_end):
            raise ValueError("waveform viewport must be finite")
        start_fraction = max(0.0, min(1.0, raw_start))
        end_fraction = max(0.0, min(1.0, raw_end))
        if end_fraction <= start_fraction:
            raise ValueError("waveform viewport must have an ordered non-empty range")

        samples = np.asarray(values)
        if samples.ndim != 2 or samples.shape[1] != 3:
            raise ValueError("waveform samples must contain exactly three axes")
        sample_count = len(samples)
        if sample_count == 0:
            empty = ((), (), ())
            return WaveformViewportProjection("raw", (), empty, empty, empty, 0, 0)

        sample_start = min(sample_count - 1, int(math.floor(start_fraction * sample_count)))
        sample_end = min(
            sample_count,
            max(sample_start + 1, int(math.ceil(end_fraction * sample_count))),
        )
        visible = np.asarray(samples[sample_start:sample_end], dtype=np.float64)
        if not np.isfinite(visible).all():
            raise ValueError("visible waveform samples must be finite")
        visible_count = len(visible)
        span = end_fraction - start_fraction

        if visible_count <= width:
            centers = (np.arange(sample_start, sample_end, dtype=np.float64) + 0.5) / sample_count
            positions = tuple(
                round(float(max(0.0, min(1.0, (center - start_fraction) / span))), 15)
                for center in centers
            )
            channels = tuple(
                tuple(float(value) for value in visible[:, axis]) for axis in range(3)
            )
            return WaveformViewportProjection(
                "raw", positions, channels, channels, channels, sample_start, sample_end
            )

        offsets = (np.arange(width + 1, dtype=np.int64) * visible_count) // width
        bucket_starts = offsets[:-1]
        minimum_rows = np.minimum.reduceat(visible, bucket_starts, axis=0)
        maximum_rows = np.maximum.reduceat(visible, bucket_starts, axis=0)
        mean_rows = np.add.reduceat(visible, bucket_starts, axis=0) / np.diff(offsets)[:, None]
        edges = sample_start + offsets
        centers = ((edges[:-1] + edges[1:]) * 0.5) / sample_count
        positions = tuple(
            round(float(max(0.0, min(1.0, (center - start_fraction) / span))), 15)
            for center in centers
        )
        minimums = tuple(
            tuple(float(value) for value in minimum_rows[:, axis]) for axis in range(3)
        )
        maximums = tuple(
            tuple(float(value) for value in maximum_rows[:, axis]) for axis in range(3)
        )
        means = tuple(
            tuple(float(value) for value in mean_rows[:, axis]) for axis in range(3)
        )
        return WaveformViewportProjection(
            "envelope", positions, minimums, maximums, means, sample_start, sample_end
        )

    def activate_annotation_template_source(
        self, recording: Recording, cycle_index: int
    ) -> tuple[Recording, AnnotationTemplate]:
        self._reject_duplicate_identity(recording.annotations)
        cycles = self._cycles(recording.annotations)
        if not 0 <= cycle_index < len(cycles):
            raise ValueError("Select one valid Cycle before Use as Reference")
        selected = cycles[cycle_index]
        touching_events = tuple(
            item
            for item in recording.annotations
            if item.kind in self._EVENT_KINDS
            and item.start_index < selected.end_index
            and selected.start_index < item.end_index
        )
        if any(
            item.start_index < selected.start_index or selected.end_index < item.end_index
            for item in touching_events
        ):
            raise ValueError("an event crosses the selected reference Cycle boundary")
        confirmed = tuple(
            replace(
                item,
                provisional=False,
                source_recording_id=None,
                source_cycle_index=None,
            )
            if item is selected
            or (
                item.kind in self._EVENT_KINDS
                and selected.start_index <= item.start_index
                and item.end_index <= selected.end_index
            )
            else item
            for item in recording.annotations
        )
        activated = replace(recording, annotations=confirmed)
        confirmed_cycles = tuple(
            item for item in self._cycles(confirmed) if not item.provisional
        )
        if len(confirmed_cycles) < 2:
            raise ValueError("Use as Reference requires at least two confirmed Cycle intervals for cadence")
        if any(item.end_index > len(recording.time_s) for item in confirmed_cycles):
            raise ValueError("a confirmed source Cycle exceeds the recording")
        self._reject_overlap(confirmed_cycles, "confirmed source Cycle intervals overlap")
        if recording.discontinuity_before is not None:
            discontinuities = np.asarray(recording.discontinuity_before, dtype=np.bool_)
            for item in (selected,) + touching_events:
                if discontinuities[item.start_index + 1 : item.end_index].any():
                    raise ValueError(f"{item.kind.value} crosses a Time Discontinuity")
        return activated, self.build_annotation_template(activated, cycle_index)

    def build_annotation_template(self, recording: Recording, cycle_index: int) -> AnnotationTemplate:
        self._reject_ignore_collision_overlap(recording.annotations)
        cycles = self._cycles(recording.annotations)
        if not 0 <= cycle_index < len(cycles):
            raise ValueError("Select one valid Cycle before Use as Reference")
        cycle = cycles[cycle_index]
        events = tuple(
            sorted(
                (
                    item
                    for item in recording.annotations
                    if item.kind in self._EVENT_KINDS
                    and cycle.start_index <= item.start_index
                    and item.end_index <= cycle.end_index
                ),
                key=lambda item: (item.start_index, item.end_index, item.kind.value),
            )
        )
        if not events:
            raise ValueError("Reference Cycle requires at least one Pick, Put, or Fork Collision event")
        self._reject_overlap(
            tuple(item for item in events if item.kind in self._POSITIVE_EVENT_KINDS),
            "Reference Cycle event intervals overlap",
        )
        duration = cycle.end_index - cycle.start_index
        starts = [item.start_index for item in cycles if not item.provisional]
        period = float(np.median(np.diff(starts))) if len(starts) >= 2 else float(duration)
        return AnnotationTemplate(
            recording.condition.robot_speed_mm_s,
            recording.recording_id,
            cycle_index,
            duration,
            period,
            tuple(
                AnnotationTemplateEvent(
                    item.kind,
                    (item.start_index - cycle.start_index) / duration,
                    (item.end_index - cycle.start_index) / duration,
                    item.reason,
                )
                for item in events
            ),
        )

    def project_annotation_template(
        self, recording: Recording, template: AnnotationTemplate
    ) -> Recording:
        if recording.condition.robot_speed_mm_s != template.robot_speed_mm_s:
            raise ValueError("annotation template Robot Speed does not match destination recording")
        retained = [item for item in recording.annotations if not item.provisional]
        cycles = self._cycles(retained)
        if len(cycles) == 1:
            anchor = cycles[0]
            generated = self._generate_cycles_from_anchor(
                anchor,
                len(recording.time_s),
                recording.recording_id,
                template,
            )
            retained.extend(generated)
            cycles = self._cycles(retained)
        proposals: list[AnnotationInterval] = []
        for cycle_index, cycle in enumerate(cycles):
            if (
                recording.recording_id == template.source_recording_id
                and cycle_index == template.source_cycle_index
            ):
                continue
            existing = [
                item
                for item in retained
                if item.kind in self._EVENT_KINDS
                and cycle.start_index <= item.start_index
                and item.end_index <= cycle.end_index
            ]
            existing_by_kind = {
                kind: sorted(
                    (item for item in existing if item.kind is kind),
                    key=lambda item: (item.start_index, item.end_index),
                )
                for kind in self._EVENT_KINDS
            }
            ordinals = {kind: 0 for kind in self._EVENT_KINDS}
            duration = cycle.end_index - cycle.start_index
            for event in template.events:
                ordinal = ordinals[event.kind]
                ordinals[event.kind] += 1
                if ordinal < len(existing_by_kind[event.kind]):
                    continue
                start = cycle.start_index + self._nearest_sample(event.start_phase * duration)
                end = cycle.start_index + self._nearest_sample(event.end_phase * duration)
                start = max(cycle.start_index, min(cycle.end_index - 1, start))
                end = max(start + 1, min(cycle.end_index, end))
                if event.kind in self._POSITIVE_EVENT_KINDS and any(
                    item.kind in self._POSITIVE_EVENT_KINDS
                    and item.start_index < end
                    and start < item.end_index
                    for item in retained + proposals
                ):
                    continue
                proposals.append(
                    AnnotationInterval(
                        event.kind,
                        start,
                        end,
                        reason=event.reason,
                        provisional=True,
                        source_recording_id=template.source_recording_id,
                        source_cycle_index=template.source_cycle_index,
                        interval_id=self._proposal_identity(
                            recording.recording_id,
                            template,
                            cycle.start_index,
                            event.kind,
                            ordinal,
                        ),
                    )
                )
        annotations = tuple(
            sorted(
                retained + proposals,
                key=lambda item: (item.start_index, item.end_index, item.kind.value),
            )
        )
        return replace(recording, annotations=annotations)

    def validate_annotations(
        self,
        sample_count: int,
        annotations: Iterable[AnnotationInterval],
        discontinuity_before: object | None = None,
    ) -> tuple[AnnotationInterval, ...]:
        items = tuple(sorted(annotations, key=lambda item: (item.start_index, item.end_index, item.kind.value)))
        self._reject_duplicate_identity(items)
        self._reject_ignore_collision_overlap(items)
        cycles = tuple(item for item in items if item.kind is ActivityKind.CYCLE)
        events = tuple(item for item in items if item.kind in self._EVENT_KINDS)
        if not cycles:
            raise ValueError("at least one Cycle interval is required")
        for item in items:
            if item.end_index > sample_count:
                raise ValueError("annotation interval exceeds the recording")
        if discontinuity_before is not None:
            discontinuities = np.asarray(discontinuity_before, dtype=np.bool_)
            if discontinuities.shape != (sample_count,):
                raise ValueError("discontinuity markers must match the recording row count")
            for item in items:
                if discontinuities[item.start_index + 1 : item.end_index].any():
                    raise ValueError(f"{item.kind.value} interval crosses a Time Discontinuity")
        self._reject_overlap(cycles, "Cycle intervals overlap")
        self._reject_overlap(
            tuple(item for item in events if item.kind in self._POSITIVE_EVENT_KINDS),
            "explicit event intervals overlap",
        )
        if len(cycles) < 2:
            raise ValueError("every recording requires at least two Cycle intervals")
        for event in events:
            containing = [cycle for cycle in cycles if cycle.start_index <= event.start_index and event.end_index <= cycle.end_index]
            if len(containing) != 1:
                raise ValueError(f"{event.kind.value} must be contained by exactly one Cycle")
        expected_counts: tuple[int, int, int] | None = None
        for cycle in cycles:
            counts = {
                kind: sum(
                    cycle.start_index <= event.start_index and event.end_index <= cycle.end_index and event.kind is kind
                    for event in events
                )
                for kind in (ActivityKind.PICK, ActivityKind.PUT, ActivityKind.FORK_COLLISION)
            }
            count_tuple = tuple(counts[kind] for kind in (ActivityKind.PICK, ActivityKind.PUT, ActivityKind.FORK_COLLISION))
            if sum(count_tuple) == 0:
                raise ValueError("every valid Cycle requires at least one Pick, Put, or Fork Collision event")
            if expected_counts is None:
                expected_counts = count_tuple
            elif count_tuple != expected_counts:
                raise ValueError("every valid Cycle must use the same Pick, Put, and Fork Collision counts")
        return items

    def derive_normal_intervals(
        self,
        recording: Recording,
        *,
        collision_response_window_s: float,
    ) -> tuple[AnnotationInterval, ...]:
        if not math.isfinite(collision_response_window_s) or collision_response_window_s <= 0:
            raise ValueError("Collision response window must be finite and greater than zero")
        items = self.validate_annotations(
            len(recording.time_s), recording.annotations, recording.discontinuity_before
        )
        times = np.asarray(recording.time_s, dtype=np.float64)
        discontinuities = (
            np.zeros(len(times), dtype=np.bool_)
            if recording.discontinuity_before is None
            else np.asarray(recording.discontinuity_before, dtype=np.bool_)
        )
        cycles = [item for item in items if item.kind is ActivityKind.CYCLE]
        excluded = [item for item in items if item.kind in self._EVENT_KINDS]
        normal: list[AnnotationInterval] = []
        for cycle in cycles:
            excluded_ranges: list[tuple[int, int]] = []
            for event in excluded:
                if event.start_index < cycle.start_index or event.end_index > cycle.end_index:
                    continue
                end = event.end_index
                if event.kind is ActivityKind.FORK_COLLISION:
                    deadline = float(times[event.start_index]) + collision_response_window_s
                    response_end = min(
                        cycle.end_index,
                        int(np.searchsorted(times, deadline + 1e-12, side="right")),
                    )
                    breaks = np.flatnonzero(
                        discontinuities[event.start_index + 1 : response_end]
                    )
                    if len(breaks):
                        response_end = event.start_index + 1 + int(breaks[0])
                    end = max(event.end_index, response_end)
                excluded_ranges.append((event.start_index, end))
            excluded_ranges.sort()
            cursor = cycle.start_index
            for start, end in excluded_ranges:
                if cursor < start:
                    normal.append(self._derived_normal(cursor, start))
                cursor = max(cursor, end)
            if cursor < cycle.end_index:
                normal.append(self._derived_normal(cursor, cycle.end_index))
        return tuple(normal)

    @staticmethod
    def _reject_ignore_collision_overlap(items: tuple[AnnotationInterval, ...]) -> None:
        collisions = tuple(item for item in items if item.kind is ActivityKind.FORK_COLLISION)
        for ignored in items:
            if ignored.kind is not ActivityKind.IGNORE:
                continue
            for collision in collisions:
                if ignored.start_index < collision.end_index and collision.start_index < ignored.end_index:
                    raise ValueError(
                        f"Ignore {ignored.interval_id} and Collision {collision.interval_id} overlap"
                    )

    @staticmethod
    def _reject_overlap(items: tuple[AnnotationInterval, ...], message: str) -> None:
        for previous, current in zip(items, items[1:]):
            if current.start_index < previous.end_index:
                raise ValueError(message)

    @staticmethod
    def _reject_duplicate_identity(items: Iterable[AnnotationInterval]) -> None:
        identities = [item.interval_id for item in items]
        if len(identities) != len(set(identities)):
            raise ValueError("annotation interval identity must be unique within a recording")

    @staticmethod
    def _derived_normal(start_index: int, end_index: int) -> AnnotationInterval:
        interval = object.__new__(AnnotationInterval)
        object.__setattr__(interval, "kind", ActivityKind.NORMAL_MOTION)
        object.__setattr__(interval, "start_index", start_index)
        object.__setattr__(interval, "end_index", end_index)
        object.__setattr__(interval, "reason", None)
        object.__setattr__(interval, "provisional", False)
        object.__setattr__(interval, "source_recording_id", None)
        object.__setattr__(interval, "source_cycle_index", None)
        object.__setattr__(interval, "interval_id", f"derived-normal:{start_index}:{end_index}")
        return interval

    @staticmethod
    def _nearest_sample(value: float) -> int:
        return int(math.floor(value + 0.5 - 1e-12))

    @staticmethod
    def _cycles(annotations: Iterable[AnnotationInterval]) -> tuple[AnnotationInterval, ...]:
        return tuple(
            sorted(
                (item for item in annotations if item.kind is ActivityKind.CYCLE),
                key=lambda item: (item.start_index, item.end_index),
            )
        )

    def _generate_cycles_from_anchor(
        self,
        anchor: AnnotationInterval,
        sample_count: int,
        destination_recording_id: str,
        template: AnnotationTemplate,
    ) -> list[AnnotationInterval]:
        generated: list[AnnotationInterval] = []
        provenance = {
            "provisional": True,
            "source_recording_id": template.source_recording_id,
            "source_cycle_index": template.source_cycle_index,
        }
        step = 1
        while True:
            start = anchor.start_index - self._nearest_sample(step * template.cycle_period_samples)
            if start < 0:
                break
            end = start + template.reference_cycle_length_samples
            if end <= anchor.start_index and not self._overlaps_any_cycle(start, end, generated):
                generated.append(
                    AnnotationInterval(
                        ActivityKind.CYCLE,
                        start,
                        end,
                        interval_id=self._proposal_identity(
                            destination_recording_id,
                            template,
                            start,
                            ActivityKind.CYCLE,
                            0,
                        ),
                        **provenance,
                    )
                )
            step += 1
        step = 1
        while True:
            start = anchor.start_index + self._nearest_sample(step * template.cycle_period_samples)
            end = start + template.reference_cycle_length_samples
            if end > sample_count:
                break
            if anchor.end_index <= start and not self._overlaps_any_cycle(start, end, generated):
                generated.append(
                    AnnotationInterval(
                        ActivityKind.CYCLE,
                        start,
                        end,
                        interval_id=self._proposal_identity(
                            destination_recording_id,
                            template,
                            start,
                            ActivityKind.CYCLE,
                            0,
                        ),
                        **provenance,
                    )
                )
            step += 1
        return generated

    @staticmethod
    def _overlaps_any_cycle(
        start_index: int,
        end_index: int,
        cycles: Iterable[AnnotationInterval],
    ) -> bool:
        return any(
            item.start_index < end_index and start_index < item.end_index
            for item in cycles
        )

    @staticmethod
    def _proposal_identity(
        destination_recording_id: str,
        template: AnnotationTemplate,
        cycle_start: int,
        kind: ActivityKind,
        ordinal: int,
    ) -> str:
        return (
            f"proposal:{destination_recording_id}:{template.source_recording_id}:"
            f"{template.source_cycle_index}:{cycle_start}:{kind.value}:{ordinal}"
        )
