from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DiagnosticStatus:
    log_path: str = ""
    previous_unclean_summary: str = ""


@dataclass(frozen=True, slots=True)
class LearningTimingEvidence:
    outer_round: int
    inner_round: int
    round_elapsed_s: float
    training_elapsed_s: float
    qualification_elapsed_s: float
    total_elapsed_s: float
    worker_attempts: tuple[tuple[int, int, float], ...]
    process_tree_peak_rss_bytes: int
    launch_available_ram_bytes: int
    worker_pids: tuple[int, ...]
