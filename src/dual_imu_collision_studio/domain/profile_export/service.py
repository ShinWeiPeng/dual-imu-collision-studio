from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import asdict

import numpy as np

from dual_imu_collision_studio.domain.profile_export.model import (
    ProfileExportRequest,
    ProfileHeaderArtifact,
    SemanticProfile,
)


class ProfileExportService:
    KERNEL_ID = re.compile(r"(?:fir-)?k[0-9]{3,}")

    def render_batch(
        self,
        profiles: tuple[SemanticProfile, ...] | list[SemanticProfile],
        language: str,
    ) -> tuple[ProfileHeaderArtifact, ...]:
        kernel_ids = [profile.kernel_id for profile in profiles]
        if len(set(kernel_ids)) != len(kernel_ids):
            raise ValueError("kernel ids must be unique within one export batch")
        artifacts: list[ProfileHeaderArtifact] = []
        for profile in profiles:
            semantic_hash = self.semantic_hash(profile)
            artifacts.append(
                ProfileHeaderArtifact(
                    profile.kernel_id,
                    self.default_filename(profile.kernel_id),
                    semantic_hash,
                    self.render(ProfileExportRequest(profile, language)),
                )
            )
        return tuple(artifacts)

    @classmethod
    def default_filename(cls, kernel_id: str) -> str:
        if cls.KERNEL_ID.fullmatch(kernel_id) is None:
            raise ValueError("kernel id must use stable kNNN form")
        return f"dual_imu_collision_profile_{kernel_id}.h"

    def render(self, request: ProfileExportRequest) -> str:
        profile = request.profile
        if request.profile.model_family != "fir":
            raise ValueError("MLP standalone export is unavailable; use desktop Replay")
        if profile.signal_channels != ("ax", "ay", "az"):
            raise ValueError("Gyroscope profiles require versioned JSON export")
        self._validate(profile)
        if request.language == "C++17":
            return self._render_cpp(profile)
        if request.language == "C99-compatible":
            return self._render_c(profile)
        raise ValueError("Header Format must be C++17 or C99-compatible")

    def semantic_hash(self, profile: SemanticProfile) -> str:
        if profile.model_family != "fir":
            raise ValueError("MLP standalone export is unavailable")
        payload = {
            "schema": profile.schema_version,
            "numeric_type": profile.numeric_type,
            "sample_rate_hz": self._number(
                profile.sample_rate_hz, profile.numeric_type
            ),
            "history_aliases_ms": profile.requested_history_aliases_ms,
            "effective_history_ms": self._number(
                profile.effective_history_ms, profile.numeric_type
            ),
            "tap_count": profile.tap_count,
            "weights": [
                self._number(value, profile.numeric_type)
                for value in np.asarray(profile.weights).flat
            ],
            "biases": [
                self._number(value, profile.numeric_type)
                for value in np.asarray(profile.biases).flat
            ],
            "ridge_alpha": self._number(profile.ridge_alpha, profile.numeric_type),
            "centers": [
                self._number(value, profile.numeric_type)
                for value in np.asarray(profile.residual_centers).flat
            ],
            "scales": [
                self._number(value, profile.numeric_type)
                for value in np.asarray(profile.residual_scales).flat
            ],
            "scale_method": profile.scale_method,
            "robust_k": profile.robust_k,
            "score_mode": profile.score_mode,
            "confirmation_mode": profile.confirmation_mode,
            "threshold": self._number(profile.threshold, profile.numeric_type),
            "threshold_comparison": "score>threshold",
            "kernel_id": profile.kernel_id,
            "outer_round": profile.outer_round,
            "inner_round": profile.inner_round,
            "initial_fit_rows": profile.initial_fit_rows,
            "refit_rows": profile.refit_rows,
            "cross_validation_fold_count": profile.cross_validation_fold_count,
            "cross_validation_evidence_level": profile.cross_validation_evidence_level,
            "cross_validation_worst_condition_mse": self._number(
                profile.cross_validation_worst_condition_mse, profile.numeric_type
            ),
            "cross_validation_pooled_mse": self._number(
                profile.cross_validation_pooled_mse, profile.numeric_type
            ),
            "worst_collision_latency_ms": self._number(
                profile.worst_collision_latency_ms, profile.numeric_type
            ),
            "combined_robustness_margin": self._number(
                profile.combined_robustness_margin, profile.numeric_type
            ),
            "false_trigger_robustness_margin": self._number(
                profile.false_trigger_robustness_margin, profile.numeric_type
            ),
            "collision_detection_robustness_margin": self._number(
                profile.collision_detection_robustness_margin, profile.numeric_type
            ),
            "covered_offsets_mm": profile.covered_offsets_mm,
            "excluded_offsets_mm": profile.excluded_offsets_mm,
            "training_speed_range": profile.training_speed_range,
            "release_ratio": self._number(0.5, profile.numeric_type),
            "release_quiet_ms": 50,
            "qualified_speed_range": profile.qualified_speed_range,
            "maximum_supplied_speed": profile.maximum_supplied_speed,
            "coverage": [
                [
                    row.robot_speed_mm_s,
                    row.collision_offset_mm,
                    row.normal_interval_count,
                    row.pick_interval_count,
                    row.put_interval_count,
                    row.collision_interval_count,
                    row.qualification_status,
                    row.recording_count,
                    row.valid_cycle_count,
                    row.normal_false_events,
                    row.pick_false_events,
                    row.put_false_events,
                    row.collision_detected_count,
                    None
                    if row.worst_collision_latency_ms is None
                    else self._number(
                        row.worst_collision_latency_ms, profile.numeric_type
                    ),
                ]
                for row in profile.coverage
            ],
            "arithmetic": "non-FMA; output-input-lag; round-to-nearest-ties-to-even; correctly-rounded-sqrt",
        }
        if profile.signal_channels != ("ax", "ay", "az"):
            payload["signal_channels"] = profile.signal_channels
        encoded = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def default_model_name(cls, profile: SemanticProfile) -> str:
        cls.default_filename(profile.kernel_id)
        if not np.isfinite(profile.sample_rate_hz) or profile.sample_rate_hz <= 0:
            raise ValueError("sample rate must be finite and positive")
        number = profile.kernel_id.removeprefix("fir-")
        return f"FIR_{profile.sample_rate_hz:g}Hz_{number}"

    @staticmethod
    def validate_model_name(model_name: str) -> None:
        if (
            not isinstance(model_name, str)
            or not model_name.strip()
            or any(unicodedata.category(char) in {"Cc", "Cs"} for char in model_name)
        ):
            raise ValueError(
                "model name must be nonblank Unicode without control characters"
            )

    def render_json(
        self,
        profile: SemanticProfile,
        model_name: str,
        *,
        input_units: str,
        source_preprocessing=None,
    ) -> str:
        """Encode one frozen qualified FIR model without a device-capacity gate."""
        if profile.model_family != "fir":
            raise ValueError("JSON deployment export supports dual-IMU FIR/Ridge only")
        if not isinstance(profile.tap_count, int) or profile.tap_count < 1:
            raise ValueError("FIR tap count must be a positive integer")
        self._validate(profile)
        if profile.confirmation_mode != "1_OF_1":
            raise ValueError(
                "JSON export requires qualification with 1_OF_1 confirmation; "
                "multi-sample confirmation cannot be changed during export"
            )
        self.validate_model_name(model_name)
        if input_units not in {"g", "m/s^2"}:
            raise ValueError("explicit acceleration input units are required")
        if profile.scale_method not in {"STD", "MAD"}:
            raise ValueError("unknown residual scale method")
        if profile.score_mode not in {"MAX_ABS", "L2_NORM"}:
            raise ValueError("unknown residual score mode")
        if not isinstance(profile.robust_k, int) or profile.robust_k < 0:
            raise ValueError("robust_k must be a nonnegative integer")

        dtype = np.dtype(profile.numeric_type)

        def numbers(values):
            with np.errstate(over="ignore", invalid="ignore"):
                result = np.asarray(values, dtype=dtype)
            if not np.all(np.isfinite(result)):
                raise ValueError(
                    "execution numbers must be finite in the selected numeric type"
                )
            return result.tolist()

        rate = float(profile.sample_rate_hz)
        if not np.isfinite(rate) or rate <= 0:
            raise ValueError("sample rate must be finite and positive")
        threshold = numbers(profile.threshold)
        scales = numbers(profile.residual_scales)
        if threshold <= 0 or any(value <= 0 for value in scales):
            raise ValueError("threshold and residual scales must be positive")
        execution = {
            "format": "collision-model-parameters",
            "schema_version": 1 if profile.signal_channels == ("ax", "ay", "az") else 2,
            "model_family": "dual_imu_fir",
            "numeric_type": profile.numeric_type,
            "required_sample_rate_hz": rate,
            "input": {
                "input_sensor": "Internal",
                "target_sensor": "External",
                "axes": ["X", "Y", "Z"]
                if profile.signal_channels == ("ax", "ay", "az")
                else list(profile.signal_channels),
                "units": input_units
                if profile.signal_channels == ("ax", "ay", "az")
                else [
                    input_units if channel.startswith("a") else "as_recorded"
                    for channel in profile.signal_channels
                ],
                "feature_order": "input_axis_then_lag",
                "weight_order": "output_axis_input_axis_lag",
                "lag_order": "current_to_past",
                "calibration": "as_recorded_during_qualification",
                "axis_transform": "none",
                "arithmetic": "non-FMA; output-input-lag; round-to-nearest-ties-to-even; correctly-rounded-sqrt",
            },
            "model": {
                "tap_count": profile.tap_count,
                "weights": numbers(profile.weights),
                "biases": numbers(profile.biases),
            },
            "preprocessing": {"mode": "bypass", "additional_model_filter": "none"},
            "residual": {
                "centers": numbers(profile.residual_centers),
                "scales": scales,
                "scale_method": profile.scale_method,
                "robust_k": profile.robust_k,
                "score_mode": profile.score_mode,
            },
            "detector": {
                "baseline_threshold": threshold,
                "confirmation_mode": profile.confirmation_mode,
                "comparison": "score>threshold",
            },
        }
        if source_preprocessing is not None:
            execution["schema_version"] = 2
            execution["preprocessing"] = {
                "mode": "mapped_model_inputs",
                "input_stage": "after_selected_preprocessing",
                "additional_model_filter": "none",
                "recordings": source_preprocessing,
            }
        canonical = json.dumps(
            execution,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        payload = execution | {
            "model_name": model_name,
            "provenance": {
                "kernel_id": profile.kernel_id,
                "source_profile_schema": profile.schema_version,
                "execution_sha256": hashlib.sha256(canonical).hexdigest(),
                "qualified_profile_sha256": self.semantic_hash(profile),
                "outer_round": profile.outer_round,
                "inner_round": profile.inner_round,
                "initial_fit_rows": profile.initial_fit_rows,
                "refit_rows": profile.refit_rows,
                "cross_validation_fold_count": profile.cross_validation_fold_count,
                "cross_validation_evidence_level": profile.cross_validation_evidence_level,
                "coverage": [asdict(row) for row in profile.coverage],
                "qualified_speed_range": profile.qualified_speed_range,
                "covered_offsets_mm": profile.covered_offsets_mm,
                "excluded_offsets_mm": profile.excluded_offsets_mm,
            },
        }
        return (
            json.dumps(
                payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False
            )
            + "\n"
        )

    def _validate(self, profile: SemanticProfile) -> None:
        if not profile.qualified:
            raise ValueError("only a qualified Profile can be exported")
        if profile.numeric_type not in {"float32", "float64"}:
            raise ValueError("Profile numeric type must be float32 or float64")
        if profile.signal_channels not in (
            ("ax", "ay", "az"),
            ("gx", "gy", "gz"),
            ("ax", "ay", "az", "gx", "gy", "gz"),
        ):
            raise ValueError("Invalid signal channel identity or order")
        channels = len(profile.signal_channels)
        weights = np.asarray(profile.weights)
        if weights.shape != (channels, channels, profile.tap_count):
            raise ValueError("weights must use [3][3][tap_count] order")
        for name, values in (
            ("biases", profile.biases),
            ("residual centers", profile.residual_centers),
            ("residual scales", profile.residual_scales),
        ):
            if np.asarray(values).shape != (channels,):
                raise ValueError(f"{name} must contain three axes")
        if not profile.coverage:
            raise ValueError("qualified condition coverage is required")
        valid_statuses = {"PASS", "FAIL", "OUT_OF_QUALIFIED_RANGE", "COVERAGE_GAP"}
        if any(
            row.qualification_status not in valid_statuses for row in profile.coverage
        ):
            raise ValueError(
                "condition coverage contains an unknown Qualification status"
            )
        if any(
            row.qualification_status != "PASS"
            for row in profile.coverage
            if row.collision_offset_mm in profile.covered_offsets_mm
            and profile.qualified_speed_range[0]
            <= row.robot_speed_mm_s
            <= profile.qualified_speed_range[1]
        ):
            raise ValueError("every tuple inside declared Profile coverage must pass")
        self.default_filename(profile.kernel_id)
        if not profile.covered_offsets_mm:
            raise ValueError("at least one covered offset is required")
        if set(profile.covered_offsets_mm) & set(profile.excluded_offsets_mm):
            raise ValueError("covered and excluded offsets must be disjoint")
        if profile.worst_collision_latency_ms > 150.0:
            raise ValueError("qualified Profile latency cannot exceed 150 ms")
        if profile.training_speed_range[0] > profile.training_speed_range[1]:
            raise ValueError("Training speed range must be ordered")
        if profile.qualified_speed_range[0] > profile.qualified_speed_range[1]:
            raise ValueError("qualified speed range must be ordered")
        margins = (
            profile.combined_robustness_margin,
            profile.false_trigger_robustness_margin,
            profile.collision_detection_robustness_margin,
        )
        if not all(np.isfinite(value) for value in margins):
            raise ValueError("Profile robustness margins must be finite")
        if (
            profile.initial_fit_rows < 1
            or profile.refit_rows < 1
            or profile.refit_rows > profile.initial_fit_rows
        ):
            raise ValueError("Profile fit/refit row provenance is invalid")
        if not 2 <= profile.cross_validation_fold_count <= 10:
            raise ValueError("Profile cross-validation fold count must be two to ten")
        if profile.cross_validation_evidence_level not in {
            "WITHIN_RECORDING_CYCLE_GROUPS",
            "WHOLE_RECORDING_PRIORITY_GROUPS",
            "BALANCED_COMPLETE_CYCLE_FOLDS",
        }:
            raise ValueError("Profile cross-validation evidence level is invalid")
        losses = (
            profile.cross_validation_worst_condition_mse,
            profile.cross_validation_pooled_mse,
        )
        if not all(
            value is not None and np.isfinite(value) and value >= 0 for value in losses
        ):
            raise ValueError(
                "Profile cross-validation losses must be finite and non-negative"
            )

    def _render_cpp(self, profile: SemanticProfile) -> str:
        scalar = "float" if profile.numeric_type == "float32" else "double"
        body = self._profile_initializer(profile, cpp=True)
        arithmetic = self._arithmetic_contract()
        return (
            "#pragma once\n#include <cstddef>\n#include <cstdint>\n\n"
            "namespace dual_imu_collision {\n"
            f"using scalar_t = {scalar};\n"
            f"inline constexpr std::size_t kTapCount = {profile.tap_count};\n"
            f"inline constexpr std::size_t kConditionCount = {len(profile.coverage)};\n"
            f"inline constexpr std::size_t kHistoryAliasCount = {len(profile.requested_history_aliases_ms)};\n"
            f"inline constexpr std::size_t kCoveredOffsetCount = {len(profile.covered_offsets_mm)};\n"
            f"inline constexpr std::size_t kExcludedOffsetCount = {len(profile.excluded_offsets_mm)};\n"
            f"inline constexpr std::size_t kExcludedOffsetStorageCount = {max(1, len(profile.excluded_offsets_mm))};\n"
            f"inline constexpr std::size_t kKernelIdSize = {len(profile.kernel_id) + 1};\n"
            f"inline constexpr std::size_t kSchemaVersionSize = {len(profile.schema_version) + 1};\n"
            "inline constexpr std::size_t kSemanticHashSize = 65;\n"
            f"inline constexpr std::size_t kArithmeticContractSize = {len(arithmetic) + 1};\n"
            'inline constexpr auto kThresholdComparison = "score>threshold";\n'
            "struct ConditionCoverage { scalar_t speed_mm_s; scalar_t offset_mm; std::uint32_t normal_count; std::uint32_t pick_count; std::uint32_t put_count; std::uint32_t collision_count; std::uint32_t qualification_status; std::uint32_t recording_count; std::uint32_t valid_cycle_count; std::uint32_t normal_false_events; std::uint32_t pick_false_events; std::uint32_t put_false_events; std::uint32_t collision_detected_count; scalar_t worst_collision_latency_ms; std::uint32_t has_worst_collision_latency; };\n"
            "struct Profile { scalar_t sample_rate_hz; scalar_t effective_history_ms; std::uint32_t tap_count; std::uint32_t requested_history_aliases_ms[kHistoryAliasCount ? kHistoryAliasCount : 1]; "
            "scalar_t weights[3][3][kTapCount]; scalar_t biases[3]; "
            "scalar_t ridge_alpha; scalar_t residual_centers[3]; scalar_t residual_scales[3]; "
            "std::uint32_t scale_method; std::uint32_t robust_k; std::uint32_t score_mode; std::uint32_t confirmation_mode; "
            "scalar_t threshold; scalar_t release_ratio; std::uint32_t release_quiet_ms; char kernel_id[kKernelIdSize]; std::uint32_t outer_round; std::uint32_t inner_round; "
            "std::uint32_t initial_fit_rows; std::uint32_t refit_rows; std::uint32_t cross_validation_fold_count; std::uint32_t cross_validation_grouping; scalar_t cross_validation_worst_condition_mse; scalar_t cross_validation_pooled_mse; "
            "scalar_t worst_collision_latency_ms; scalar_t combined_robustness_margin; scalar_t false_trigger_robustness_margin; "
            "scalar_t collision_detection_robustness_margin; scalar_t covered_offsets_mm[kCoveredOffsetCount]; "
            "scalar_t excluded_offsets_mm[kExcludedOffsetStorageCount]; std::uint32_t excluded_offset_count; scalar_t training_min_speed; scalar_t training_max_speed; scalar_t qualified_min_speed; "
            "scalar_t qualified_max_speed; scalar_t maximum_supplied_speed; ConditionCoverage coverage[kConditionCount]; "
            "char schema_version[kSchemaVersionSize]; char semantic_hash[kSemanticHashSize]; char arithmetic_contract[kArithmeticContractSize]; };\n"
            f"inline constexpr Profile kProfile = {body};\n"
            "static_assert(sizeof(kProfile.weights) / sizeof(kProfile.weights[0]) == 3);\n"
            "}  // namespace dual_imu_collision\n"
        )

    def _render_c(self, profile: SemanticProfile) -> str:
        scalar = "float" if profile.numeric_type == "float32" else "double"
        body = self._profile_initializer(profile, cpp=False)
        arithmetic = self._arithmetic_contract()
        return (
            "#ifndef DUAL_IMU_COLLISION_PROFILE_H\n#define DUAL_IMU_COLLISION_PROFILE_H\n"
            "#include <stdint.h>\n\n"
            f"#define DUAL_IMU_COLLISION_TAP_COUNT {profile.tap_count}\n"
            f"#define DUAL_IMU_COLLISION_CONDITION_COUNT {len(profile.coverage)}\n"
            f"#define DUAL_IMU_COLLISION_HISTORY_ALIAS_COUNT {len(profile.requested_history_aliases_ms)}\n"
            f"#define DUAL_IMU_COLLISION_COVERED_OFFSET_COUNT {len(profile.covered_offsets_mm)}\n"
            f"#define DUAL_IMU_COLLISION_EXCLUDED_OFFSET_COUNT {len(profile.excluded_offsets_mm)}\n"
            f"#define DUAL_IMU_COLLISION_EXCLUDED_OFFSET_STORAGE_COUNT {max(1, len(profile.excluded_offsets_mm))}\n"
            f"#define DUAL_IMU_COLLISION_KERNEL_ID_SIZE {len(profile.kernel_id) + 1}\n"
            f"#define DUAL_IMU_COLLISION_SCHEMA_VERSION_SIZE {len(profile.schema_version) + 1}\n"
            "#define DUAL_IMU_COLLISION_SEMANTIC_HASH_SIZE 65\n"
            f"#define DUAL_IMU_COLLISION_ARITHMETIC_CONTRACT_SIZE {len(arithmetic) + 1}\n"
            '#define DUAL_IMU_COLLISION_THRESHOLD_COMPARISON "score>threshold"\n'
            f"typedef {scalar} dual_imu_collision_scalar_t;\n"
            "typedef struct { dual_imu_collision_scalar_t speed_mm_s; dual_imu_collision_scalar_t offset_mm; uint32_t normal_count; uint32_t pick_count; uint32_t put_count; uint32_t collision_count; uint32_t qualification_status; uint32_t recording_count; uint32_t valid_cycle_count; uint32_t normal_false_events; uint32_t pick_false_events; uint32_t put_false_events; uint32_t collision_detected_count; dual_imu_collision_scalar_t worst_collision_latency_ms; uint32_t has_worst_collision_latency; } dual_imu_collision_condition_coverage_t;\n"
            "typedef struct { dual_imu_collision_scalar_t sample_rate_hz; dual_imu_collision_scalar_t effective_history_ms; uint32_t tap_count; uint32_t requested_history_aliases_ms[DUAL_IMU_COLLISION_HISTORY_ALIAS_COUNT ? DUAL_IMU_COLLISION_HISTORY_ALIAS_COUNT : 1]; "
            "dual_imu_collision_scalar_t weights[3][3][DUAL_IMU_COLLISION_TAP_COUNT]; dual_imu_collision_scalar_t biases[3]; "
            "dual_imu_collision_scalar_t ridge_alpha; dual_imu_collision_scalar_t residual_centers[3]; dual_imu_collision_scalar_t residual_scales[3]; "
            "uint32_t scale_method; uint32_t robust_k; uint32_t score_mode; uint32_t confirmation_mode; dual_imu_collision_scalar_t threshold; "
            "dual_imu_collision_scalar_t release_ratio; uint32_t release_quiet_ms; char kernel_id[DUAL_IMU_COLLISION_KERNEL_ID_SIZE]; uint32_t outer_round; uint32_t inner_round; "
            "uint32_t initial_fit_rows; uint32_t refit_rows; uint32_t cross_validation_fold_count; uint32_t cross_validation_grouping; dual_imu_collision_scalar_t cross_validation_worst_condition_mse; dual_imu_collision_scalar_t cross_validation_pooled_mse; "
            "dual_imu_collision_scalar_t worst_collision_latency_ms; dual_imu_collision_scalar_t combined_robustness_margin; "
            "dual_imu_collision_scalar_t false_trigger_robustness_margin; dual_imu_collision_scalar_t collision_detection_robustness_margin; "
            "dual_imu_collision_scalar_t covered_offsets_mm[DUAL_IMU_COLLISION_COVERED_OFFSET_COUNT]; "
            "dual_imu_collision_scalar_t excluded_offsets_mm[DUAL_IMU_COLLISION_EXCLUDED_OFFSET_STORAGE_COUNT]; uint32_t excluded_offset_count; dual_imu_collision_scalar_t training_min_speed; dual_imu_collision_scalar_t training_max_speed; "
            "dual_imu_collision_scalar_t qualified_min_speed; "
            "dual_imu_collision_scalar_t qualified_max_speed; dual_imu_collision_scalar_t maximum_supplied_speed; "
            "dual_imu_collision_condition_coverage_t coverage[DUAL_IMU_COLLISION_CONDITION_COUNT]; char schema_version[DUAL_IMU_COLLISION_SCHEMA_VERSION_SIZE]; "
            "char semantic_hash[DUAL_IMU_COLLISION_SEMANTIC_HASH_SIZE]; char arithmetic_contract[DUAL_IMU_COLLISION_ARITHMETIC_CONTRACT_SIZE]; } dual_imu_collision_profile_t;\n"
            f"static const dual_imu_collision_profile_t dual_imu_collision_profile = {body};\n"
            "#endif\n"
        )

    def _profile_initializer(self, profile: SemanticProfile, *, cpp: bool) -> str:
        weights = np.asarray(profile.weights)
        weight_text = (
            "{"
            + ",".join(
                "{"
                + ",".join(
                    "{"
                    + ",".join(
                        self._literal(value, profile.numeric_type)
                        for value in weights[o, i]
                    )
                    + "}"
                    for i in range(3)
                )
                + "}"
                for o in range(3)
            )
            + "}"
        )
        array_wrap = lambda value: "{" + value + "}"
        vec = lambda values: (
            "{"
            + ",".join(self._literal(value, profile.numeric_type) for value in values)
            + "}"
        )
        coverage = (
            "{"
            + ",".join(
                "{"
                + ",".join(
                    [
                        self._literal(row.robot_speed_mm_s, profile.numeric_type),
                        self._literal(row.collision_offset_mm, profile.numeric_type),
                        str(row.normal_interval_count),
                        str(row.pick_interval_count),
                        str(row.put_interval_count),
                        str(row.collision_interval_count),
                        str(
                            {
                                "PASS": 1,
                                "FAIL": 2,
                                "OUT_OF_QUALIFIED_RANGE": 3,
                                "COVERAGE_GAP": 4,
                            }[row.qualification_status]
                        ),
                        str(row.recording_count),
                        str(row.valid_cycle_count),
                        str(row.normal_false_events),
                        str(row.pick_false_events),
                        str(row.put_false_events),
                        str(row.collision_detected_count),
                        self._literal(
                            row.worst_collision_latency_ms or 0.0, profile.numeric_type
                        ),
                        "1" if row.worst_collision_latency_ms is not None else "0",
                    ]
                )
                + "}"
                for row in profile.coverage
            )
            + "}"
        )
        excluded_offsets = profile.excluded_offsets_mm or (0.0,)
        values = [
            self._literal(profile.sample_rate_hz, profile.numeric_type),
            self._literal(profile.effective_history_ms, profile.numeric_type),
            str(profile.tap_count),
            "{"
            + ",".join(
                str(value) for value in (profile.requested_history_aliases_ms or (0,))
            )
            + "}",
            weight_text,
            vec(profile.biases),
            self._literal(profile.ridge_alpha, profile.numeric_type),
            vec(profile.residual_centers),
            vec(profile.residual_scales),
            str({"STD": 1, "MAD": 2}[profile.scale_method]),
            str(profile.robust_k),
            str({"MAX_ABS": 1, "L2_NORM": 2}[profile.score_mode]),
            str(
                {"1_OF_1": 1, "2_CONSECUTIVE": 2, "2_OF_3": 3}[
                    profile.confirmation_mode
                ]
            ),
            self._literal(profile.threshold, profile.numeric_type),
            self._literal(0.5, profile.numeric_type),
            "50",
            f'"{profile.kernel_id}"',
            str(profile.outer_round),
            str(profile.inner_round),
            str(profile.initial_fit_rows),
            str(profile.refit_rows),
            str(profile.cross_validation_fold_count),
            str(
                {
                    "WITHIN_RECORDING_CYCLE_GROUPS": 1,
                    "WHOLE_RECORDING_PRIORITY_GROUPS": 2,
                    "BALANCED_COMPLETE_CYCLE_FOLDS": 3,
                }[profile.cross_validation_evidence_level]
            ),
            self._literal(
                profile.cross_validation_worst_condition_mse, profile.numeric_type
            ),
            self._literal(profile.cross_validation_pooled_mse, profile.numeric_type),
            self._literal(profile.worst_collision_latency_ms, profile.numeric_type),
            self._literal(profile.combined_robustness_margin, profile.numeric_type),
            self._literal(
                profile.false_trigger_robustness_margin, profile.numeric_type
            ),
            self._literal(
                profile.collision_detection_robustness_margin, profile.numeric_type
            ),
            vec(profile.covered_offsets_mm),
            vec(excluded_offsets),
            str(len(profile.excluded_offsets_mm)),
            self._literal(profile.training_speed_range[0], profile.numeric_type),
            self._literal(profile.training_speed_range[1], profile.numeric_type),
            self._literal(profile.qualified_speed_range[0], profile.numeric_type),
            self._literal(profile.qualified_speed_range[1], profile.numeric_type),
            self._literal(profile.maximum_supplied_speed, profile.numeric_type),
            coverage,
            f'"{profile.schema_version}"',
            f'"{self.semantic_hash(profile)}"',
            f'"{self._arithmetic_contract()}"',
        ]
        return "{" + ",".join(values) + "}"

    @staticmethod
    def _number(value: object, numeric_type: str) -> str:
        if numeric_type == "float32":
            return format(float(np.float32(value)), ".9g")
        return format(float(np.float64(value)), ".17g")

    def _literal(self, value: object, numeric_type: str) -> str:
        suffix = "f" if numeric_type == "float32" else ""
        text = self._number(value, numeric_type)
        if "e" not in text.lower() and "." not in text:
            text += ".0"
        return text + suffix

    @staticmethod
    def _arithmetic_contract() -> str:
        return "non-FMA; output-input-lag; round-to-nearest-ties-to-even; correctly-rounded-sqrt"
