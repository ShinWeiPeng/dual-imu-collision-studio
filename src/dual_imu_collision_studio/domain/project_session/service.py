from __future__ import annotations

import math
from decimal import Decimal
from collections.abc import Mapping, Sequence

from .model import ProjectDocument, ProjectSourceReference


class ProjectSessionService:
    FORMAT = "dual-imu-collision-studio-project"
    SCHEMA_VERSION = 2
    ALGORITHM_CONTRACT = "dual-imu-collision-profile/2"
    RESULT_CONTRACT = "semantic-profile/2"
    ACTIVITY_KINDS = {
        "Cycle",
        "Robot Pick",
        "Robot Put",
        "Robot Fork Collision",
        "Ignore",
    }
    NUMERIC_TYPES = {"", "float32", "float64"}
    FORBIDDEN_WAVEFORM_KEYS = {
        "time_s",
        "internal_imu",
        "external_imu",
        "waveform",
        "waveforms",
        "waveform_samples",
        "sample_rows",
        "normalized_samples",
    }
    PROFILE_FIELDS = {
        "schema_version",
        "numeric_type",
        "sample_rate_hz",
        "requested_history_aliases_ms",
        "effective_history_ms",
        "tap_count",
        "weights",
        "biases",
        "ridge_alpha",
        "residual_centers",
        "residual_scales",
        "scale_method",
        "robust_k",
        "score_mode",
        "confirmation_mode",
        "threshold",
        "kernel_id",
        "worst_collision_latency_ms",
        "combined_robustness_margin",
        "false_trigger_robustness_margin",
        "collision_detection_robustness_margin",
        "covered_offsets_mm",
        "excluded_offsets_mm",
        "training_speed_range",
        "qualified_speed_range",
        "maximum_supplied_speed",
        "coverage",
        "qualified",
        "outer_round",
        "inner_round",
        "initial_fit_rows",
        "refit_rows",
        "cross_validation_fold_count",
        "cross_validation_evidence_level",
        "cross_validation_worst_condition_mse",
        "cross_validation_pooled_mse",
    }
    COVERAGE_FIELDS = {
        "robot_speed_mm_s",
        "collision_offset_mm",
        "normal_interval_count",
        "pick_interval_count",
        "put_interval_count",
        "collision_interval_count",
        "qualification_status",
        "recording_count",
        "valid_cycle_count",
        "normal_false_events",
        "pick_false_events",
        "put_false_events",
        "collision_detected_count",
        "worst_collision_latency_ms",
    }

    def validate(self, document: ProjectDocument) -> ProjectDocument:
        data = document.data
        self._mapping(data, "project root")
        self._reject_waveform_payload(data, "project")
        self._finite_tree(data, "project")
        if "training_selection" in data:
            selection = self._mapping(data["training_selection"], "Training selection")
            algorithms = self._sequence(
                selection.get("algorithms"), "Training algorithms"
            )
            if list(algorithms) != [
                a for a in ("fir", "mlp", "var") if a in algorithms
            ]:
                raise ValueError("Unknown or duplicate Training algorithm")
            sources = self._mapping(selection.get("sources"), "Training sources")
            if set(sources) != {"fir", "mlp", "var"} or any(
                sources[a]
                not in ({"internal", "external"} if a == "var" else {"raw", "filtered"})
                for a in sources
            ):
                raise ValueError("Invalid Training source selection")
        required = {
            "format",
            "schema_version",
            "algorithm_contract",
            "result_contract",
            "recordings",
            "annotation_templates",
            "reviewed_duplicate_keys",
            "selected_recording",
            "selected_stage",
            "annotations_ready",
            "numeric_type",
        }
        missing = sorted(required - set(data))
        if missing:
            raise ValueError(
                "project is missing required fields: " + ", ".join(missing)
            )
        if data["format"] != self.FORMAT:
            raise ValueError("unsupported project format")
        if data["schema_version"] != self.SCHEMA_VERSION:
            raise ValueError("unsupported project schema version")
        if data["algorithm_contract"] != self.ALGORITHM_CONTRACT:
            raise ValueError("unsupported algorithm contract version")
        if data["result_contract"] != self.RESULT_CONTRACT:
            raise ValueError("unsupported result contract version")
        if data["numeric_type"] not in self.NUMERIC_TYPES:
            raise ValueError("unknown Target Numeric Type")
        if not isinstance(data["annotations_ready"], bool):
            raise ValueError("annotations_ready must be boolean")
        recordings = self._sequence(data["recordings"], "recordings")
        recording_ids: set[str] = set()
        for index, raw in enumerate(recordings):
            recording = self._mapping(raw, f"recordings[{index}]")
            self._validate_recording(recording, recording_ids, index)
        selected = self._integer(data["selected_recording"], "selected_recording")
        if selected < -1 or selected >= len(recordings):
            raise ValueError("selected_recording is outside the recording list")
        stage = self._integer(data["selected_stage"], "selected_stage")
        if not 0 <= stage <= 4:
            raise ValueError("selected_stage must be between zero and four")
        for index, raw in enumerate(
            self._sequence(data["annotation_templates"], "annotation_templates")
        ):
            template = self._mapping(raw, f"annotation_templates[{index}]")
            if template.get("source_recording_id") not in recording_ids:
                raise ValueError("annotation template references an unknown recording")
            if (
                self._number(template.get("robot_speed_mm_s"), "template Robot Speed")
                <= 0
            ):
                raise ValueError("template Robot Speed must be positive")
            self._integer(template.get("source_cycle_index"), "template source Cycle")
            if (
                self._integer(
                    template.get("reference_cycle_length_samples"),
                    "template Cycle length",
                )
                <= 0
            ):
                raise ValueError("template Cycle length must be positive")
            if (
                self._number(template.get("cycle_period_samples"), "template cadence")
                <= 0
            ):
                raise ValueError("template cadence must be positive")
            for event in self._sequence(template.get("events"), "template events"):
                event_map = self._mapping(event, "template event")
                if event_map.get("kind") not in self.ACTIVITY_KINDS - {"Cycle"}:
                    raise ValueError("unknown template event kind")
                start = self._number(
                    event_map.get("start_phase"), "template event start"
                )
                end = self._number(event_map.get("end_phase"), "template event end")
                if not 0 <= start < end <= 1:
                    raise ValueError(
                        "template event phases must be ordered within one Cycle"
                    )
                if (
                    event_map.get("kind") == "Ignore"
                    and not str(event_map.get("reason", "")).strip()
                ):
                    raise ValueError("template Ignore event requires a reason")
        for raw in self._sequence(
            data["reviewed_duplicate_keys"], "reviewed_duplicate_keys"
        ):
            key = self._sequence(raw, "reviewed duplicate condition")
            if len(key) != 3:
                raise ValueError(
                    "reviewed duplicate conditions require Sample Rate, Speed, and Offset"
                )
            if any(
                self._number(value, "reviewed duplicate condition") <= 0
                for value in key[:2]
            ):
                raise ValueError(
                    "reviewed duplicate Sample Rate and Speed must be positive"
                )
        if "results" in data:
            if not data["annotations_ready"] or not data["numeric_type"]:
                raise ValueError(
                    "completed results require confirmed annotations and a Target Numeric Type"
                )
            self._validate_results(self._mapping(data["results"], "results"), data)
        self._validate_learning_provenance(data)
        return document

    def _strict_fields(self, raw, fields, name):
        value = self._mapping(raw, name)
        if set(value) != set(fields.split()):
            raise ValueError(f"{name} has missing or unknown fields")
        return value

    def _validate_captured_settings(self, raw, *, require_fixed_selections=True):
        settings = self._mapping(raw, "captured Learning settings")
        legacy_fields = {
            "n_fold",
            "include_training_mse",
            "use_robust_refit",
            "convergence_tolerance_percent",
            "validation_allowance_percent",
        }
        extended_fields = legacy_fields | {
            "training_mode",
            "fixed_history_ms",
            "fixed_ridge_alphas",
        }
        mlp_fields = extended_fields | {
            "model_families",
            "mlp_history_ms",
            "mlp_layer_widths",
            "mlp_l2",
        }
        field_names = frozenset(settings)
        if field_names not in {
            frozenset(legacy_fields),
            frozenset(extended_fields),
            frozenset(mlp_fields),
        }:
            raise ValueError("captured Learning settings has missing or unknown fields")
        if not 2 <= self._integer(settings["n_fold"], "N-fold") <= 10:
            raise ValueError("captured N-fold is outside 2 through 10")
        for flag in ("include_training_mse", "use_robust_refit"):
            if type(settings[flag]) is not bool:
                raise ValueError("captured Learning option must be boolean")
        for name, minimum in (
            ("convergence_tolerance_percent", 0.001),
            ("validation_allowance_percent", 0),
        ):
            value = self._number(settings[name], name)
            if not minimum <= value <= 100 or Decimal(str(value)) != Decimal(
                str(value)
            ).quantize(Decimal(".001")):
                raise ValueError("invalid captured Learning percentage")
        if field_names in {frozenset(extended_fields), frozenset(mlp_fields)}:
            mode = settings["training_mode"]
            if mode not in {"fixed_grid", "optimized"}:
                raise ValueError("invalid captured Training mode")
            histories = tuple(
                self._sequence(settings["fixed_history_ms"], "fixed History selection")
            )
            alphas = tuple(
                self._sequence(
                    settings["fixed_ridge_alphas"], "fixed Ridge alpha selection"
                )
            )
            history_options = (4, 8, 16, 32, 64, 128)
            alpha_options = (1e-6, 1e-4, 1e-2, 1.0, 100.0)
            if histories != tuple(
                value for value in history_options if value in histories
            ):
                raise ValueError("invalid fixed History selection")
            if alphas != tuple(value for value in alpha_options if value in alphas):
                raise ValueError("invalid fixed Ridge alpha selection")
            if (
                mode == "fixed_grid"
                and require_fixed_selections
                and "fir" in settings.get("model_families", ["fir"])
                and (not histories or not alphas)
            ):
                raise ValueError(
                    "captured fixed-grid run requires History and Ridge alpha selections"
                )
            if mode == "fixed_grid" and settings["use_robust_refit"]:
                raise ValueError("captured fixed-grid run cannot use Robust refit")
        if field_names == frozenset(mlp_fields):
            families = tuple(
                self._sequence(settings["model_families"], "model families")
            )
            if families != tuple(f for f in ("fir", "mlp") if f in families):
                raise ValueError("invalid model family selection")
            groups = self._sequence(settings["mlp_layer_widths"], "MLP hidden layers")
            if not groups:
                raise ValueError("MLP needs a positive hidden depth")
            selections = [
                (settings["mlp_history_ms"], (4, 8, 16, 32, 64, 128)),
                (settings["mlp_l2"], (0.0001, 0.001, 0.01)),
            ]
            selections.extend((group, (4, 8, 16, 32, 64, 128)) for group in groups)
            for raw_selection, options in selections:
                selection = tuple(self._sequence(raw_selection, "MLP selection"))
                if selection != tuple(v for v in options if v in selection):
                    raise ValueError("invalid MLP parameter selection")
                if require_fixed_selections and "mlp" in families and not selection:
                    raise ValueError("MLP run requires every parameter selection")
            if require_fixed_selections and not families:
                raise ValueError("run requires a model family")
        return settings

    def _validate_saved_fold_plan(self, raw, settings, recordings, offsets, speeds):
        plan = self._strict_fields(raw, "fold_count evidence_level folds", "fold plan")
        n = settings["n_fold"]
        folds = self._sequence(plan["folds"], "folds")
        if (
            type(plan["fold_count"]) is not int
            or plan["fold_count"] != n
            or len(folds) != n
            or plan["evidence_level"] != "BALANCED_COMPLETE_CYCLE_FOLDS"
        ):
            raise ValueError("saved fold plan does not match captured settings")
        expected = {}
        for rec in recordings:
            if (
                rec["confirmed"]
                and rec["collision_offset_mm"] in offsets
                and rec["robot_speed_mm_s"] in speeds
            ):
                cycles = [a for a in rec["annotations"] if a["kind"] == "Cycle"]
                if len(cycles) < 2:
                    raise ValueError(
                        "saved fold recording requires at least two Cycles"
                    )
                for cycle in range(len(cycles)):
                    expected[(rec["recording_id"], cycle)] = (
                        rec["robot_speed_mm_s"],
                        rec["collision_offset_mm"],
                    )
        keys = set(expected.values())
        if not keys:
            raise ValueError("saved fold plan has no source Cycles")
        seen, roles, counts = set(), {}, {key: [] for key in keys}
        for index, raw_fold in enumerate(folds, 1):
            fold = self._strict_fields(raw_fold, "fold_index held_out_groups", "fold")
            if self._integer(fold["fold_index"], "fold index") != index:
                raise ValueError("saved fold indexes must be complete and ordered")
            per_condition = dict.fromkeys(keys, 0)
            for raw_group in self._sequence(fold["held_out_groups"], "fold groups"):
                group = self._strict_fields(
                    raw_group,
                    "recording_id robot_speed_mm_s collision_offset_mm cycle_index",
                    "fold group",
                )
                identity = (
                    group["recording_id"],
                    self._integer(group["cycle_index"], "Cycle index"),
                )
                key = (
                    self._number(group["robot_speed_mm_s"], "fold speed"),
                    self._number(group["collision_offset_mm"], "fold offset"),
                )
                if (
                    not isinstance(identity[0], str)
                    or identity in seen
                    or expected.get(identity) != key
                ):
                    raise ValueError(
                        "saved fold group has unknown, duplicate or inconsistent Cycle identity"
                    )
                seen.add(identity)
                per_condition[key] += 1
                roles.setdefault(identity[0], set()).add(index)
            if any(value == 0 for value in per_condition.values()):
                raise ValueError("every saved fold requires every active condition")
            for key, value in per_condition.items():
                counts[key].append(value)
        if seen != set(expected) or any(len(value) < 2 for value in roles.values()):
            raise ValueError(
                "saved folds must cover every Cycle once and retain Training in every recording"
            )
        if any(max(value) - min(value) > 1 for value in counts.values()):
            raise ValueError("saved folds are not balanced by condition")
        return keys

    def _validate_learning_provenance(self, data):
        if "algorithm_runs" in data:
            runs = self._mapping(data["algorithm_runs"], "algorithm runs")
            profiles = data.get("results", {}).get("profiles", [])
            evidence = data.get("kernel_training_evidence", {})
            assigned_profiles, assigned_evidence = set(), set()
            for key, saved in runs.items():
                saved = self._mapping(saved, "saved algorithm run")
                if key not in {"fir", "mlp", "var"}:
                    raise ValueError("Unknown saved algorithm")
                choice = self._mapping(saved.get("choice"), "algorithm source")
                if choice.get("algorithm") != key or choice.get("source") not in (
                    {"internal", "external"} if key == "var" else {"raw", "filtered"}
                ):
                    raise ValueError("Invalid saved algorithm source")
                identities = self._sequence(
                    saved.get("candidate_ids"), "algorithm candidate identities"
                )
                if len(set(identities)) != len(identities) or any(
                    not isinstance(v, str) or not v for v in identities
                ):
                    raise ValueError("Invalid algorithm candidate identities")
                if assigned_profiles.intersection(
                    identities
                ) or assigned_evidence.intersection(identities):
                    raise ValueError("Candidate assigned to multiple algorithms")
                subset = [p for p in profiles if p["kernel_id"] in identities]
                if any(
                    p.get("model_family", "fir")
                    != ("self_ridge" if key == "var" else key)
                    for p in subset
                ):
                    raise ValueError("Saved algorithm differs from model family")
                ev = {k: v for k, v in evidence.items() if k in identities}
                assigned_profiles.update(p["kernel_id"] for p in subset)
                assigned_evidence.update(ev)
                proxy = dict(data)
                del proxy["algorithm_runs"]
                proxy.update(
                    learning_run_provenance=saved.get("learning_run_provenance"),
                    learning_family_provenance=saved.get(
                        "learning_family_provenance", []
                    ),
                    kernel_training_evidence=ev,
                )
                proxy["results"] = dict(data.get("results", {}), profiles=subset)
                self._validate_learning_provenance(proxy)
            if assigned_profiles != {
                p["kernel_id"] for p in profiles
            } or assigned_evidence != set(evidence):
                raise ValueError("Saved results lack algorithm source provenance")
            return
        family_runs = self._sequence(
            data.get("learning_family_provenance", []), "family provenance"
        )
        if family_runs:
            families = [run.get("family") for run in family_runs]
            if families != [f for f in ("fir", "mlp") if f in families]:
                raise ValueError("invalid or duplicate family provenance")
            if data.get("learning_run_provenance") != family_runs[0]:
                raise ValueError("primary provenance differs from family provenance")
            evidence = data.get("kernel_training_evidence", {})
            assigned = set()
            profiles = data.get("results", {}).get("profiles", [])
            if any(
                (
                    "fir"
                    if p.get("model_family") == "self_ridge"
                    else p.get("model_family", "fir")
                )
                not in families
                for p in profiles
            ):
                raise ValueError("Profile lacks family provenance")
            for run in family_runs:
                family = run["family"]
                if tuple(run["settings"].get("model_families", ())) != (family,):
                    raise ValueError("family run settings must select its own model")
                subset = {
                    k: v
                    for k, v in evidence.items()
                    if tuple(v["settings"].get("model_families", ())) == (family,)
                }
                assigned.update(subset)
                proxy = dict(
                    data,
                    learning_family_provenance=[],
                    learning_run_provenance=run,
                    kernel_training_evidence=subset,
                )
                proxy["results"] = dict(
                    data.get("results", {}),
                    profiles=[
                        p
                        for p in profiles
                        if (
                            "fir"
                            if p.get("model_family") == "self_ridge"
                            else p.get("model_family", "fir")
                        )
                        == family
                    ],
                )
                self._validate_learning_provenance(proxy)
            if assigned != set(evidence):
                raise ValueError("kernel evidence lacks family provenance")
            return
        evidence_map = self._mapping(
            data.get("kernel_training_evidence", {}), "kernel training evidence"
        )
        raw = data.get("learning_run_provenance")
        if raw is None:
            if evidence_map:
                raise ValueError("kernel training evidence requires run provenance")
            if any(
                p.get("cross_validation_evidence_level")
                == "BALANCED_COMPLETE_CYCLE_FOLDS"
                for p in data.get("results", {}).get("profiles", ())
            ):
                raise ValueError("new fold Profile requires original run provenance")
            return  # Historical projects must not acquire fabricated training evidence.
        run = self._strict_fields(
            raw,
            "seed settings rounds sampler_version"
            + (" family" if "family" in raw else ""),
            "Learning run provenance",
        )
        if run.get("family", "fir") not in {"fir", "mlp"}:
            raise ValueError("unknown provenance family")
        settings = self._validate_captured_settings(run["settings"])
        if (
            not 0 <= self._integer(run["seed"], "run seed") < 2**64
            or run["sampler_version"] != "balanced-cycle-permutation/1"
        ):
            raise ValueError("unsupported Learning sampler provenance")
        rounds, round_keys, round_ids = {}, {}, set()
        for raw_round in self._sequence(run["rounds"], "Learning rounds"):
            item = self._strict_fields(
                raw_round,
                "outer_round inner_round seed active_offsets training_speeds fold_plan",
                "Learning round",
            )
            identity = tuple(
                self._integer(item[name], name)
                for name in ("outer_round", "inner_round")
            )
            if min(identity) < 1 or identity in round_ids:
                raise ValueError("duplicate or invalid Learning round identity")
            round_ids.add(identity)
            seed = self._integer(item["seed"], "round seed")
            if not 0 <= seed < 2**64:
                raise ValueError("invalid round seed")
            offsets = tuple(
                self._number(v, "active offset")
                for v in self._sequence(item["active_offsets"], "active offsets")
            )
            speeds = tuple(
                self._number(v, "training speed")
                for v in self._sequence(item["training_speeds"], "training speeds")
            )
            if (
                not offsets
                or not speeds
                or offsets != tuple(sorted(set(offsets)))
                or speeds != tuple(sorted(set(speeds)))
            ):
                raise ValueError("invalid saved Learning scope")
            keys = self._validate_saved_fold_plan(
                item["fold_plan"], settings, data["recordings"], offsets, speeds
            )
            # A random seed may repeat; pair it with its actual immutable plan.
            rounds[identity] = item
            round_keys[identity] = keys
        for kernel_id, raw_evidence in evidence_map.items():
            if not isinstance(kernel_id, str) or not kernel_id:
                raise ValueError("invalid kernel evidence identity")
            evidence = self._strict_fields(
                raw_evidence,
                "settings fold_index conditions parameter_loss kernel_loss round_seed fold_plan",
                "kernel training evidence",
            )
            if evidence["settings"] != settings:
                raise ValueError("kernel settings differ from captured run settings")
            matches = [
                identity
                for identity, item in rounds.items()
                if item["seed"] == evidence["round_seed"]
                and item["fold_plan"] == evidence["fold_plan"]
            ]
            if (
                not matches
                or not 1
                <= self._integer(evidence["fold_index"], "kernel fold")
                <= settings["n_fold"]
            ):
                raise ValueError("kernel evidence references an unknown round or fold")
            keys, losses = [], []
            for raw_condition in self._sequence(
                evidence["conditions"], "kernel conditions"
            ):
                condition = self._strict_fields(
                    raw_condition,
                    "robot_speed_mm_s collision_offset_mm training_mse validation_mse training_sample_count validation_sample_count",
                    "kernel condition",
                )
                keys.append(
                    (
                        self._number(condition["robot_speed_mm_s"], "condition speed"),
                        self._number(
                            condition["collision_offset_mm"], "condition offset"
                        ),
                    )
                )
                training = self._number(condition["training_mse"], "Training MSE")
                validation = self._number(condition["validation_mse"], "Validation MSE")
                if min(training, validation) < 0 or validation > training * (
                    1 + settings["validation_allowance_percent"] / 100
                ):
                    raise ValueError("saved retained kernel fails Validation")
                if any(
                    self._integer(condition[name], name) <= 0
                    for name in ("training_sample_count", "validation_sample_count")
                ):
                    raise ValueError("saved MSE requires positive sample counts")
                losses.append(
                    0.5 * training + 0.5 * validation
                    if settings["include_training_mse"]
                    else validation
                )
            if len(keys) != len(set(keys)) or set(keys) != round_keys[matches[0]]:
                raise ValueError("kernel evidence condition coverage mismatch")
            if (
                self._number(evidence["kernel_loss"], "kernel Loss") != max(losses)
                or self._number(evidence["parameter_loss"], "parameter Loss") < 0
            ):
                raise ValueError("saved kernel Loss is inconsistent")

        for raw_profile in data.get("results", {}).get("profiles", ()):
            if (
                raw_profile.get("cross_validation_evidence_level")
                != "BALANCED_COMPLETE_CYCLE_FOLDS"
            ):
                continue
            evidence = evidence_map.get(raw_profile["kernel_id"])
            if (
                evidence is None
                or raw_profile["cross_validation_fold_count"] != settings["n_fold"]
            ):
                raise ValueError(
                    "new fold Profile requires its original kernel evidence"
                )
            if (
                raw_profile["cross_validation_worst_condition_mse"]
                != evidence["parameter_loss"]
            ):
                raise ValueError(
                    "Profile selection Loss differs from original kernel evidence"
                )
            if (
                "fir"
                if raw_profile.get("model_family") == "self_ridge"
                else raw_profile.get("model_family", "fir")
            ) != run.get("family", "fir"):
                raise ValueError("Profile family differs from run provenance")
            if raw_profile.get("model_family") == "mlp":
                widths = [len(b) for b in raw_profile["biases"][:-1]]
                selected = settings["mlp_layer_widths"]
                if len(widths) != len(selected) or any(
                    w not in choices for w, choices in zip(widths, selected)
                ):
                    raise ValueError(
                        "MLP architecture differs from captured selections"
                    )
                if raw_profile["ridge_alpha"] not in settings["mlp_l2"]:
                    raise ValueError("MLP L2 differs from captured selections")
                expected_aliases = [
                    ms
                    for ms in settings["mlp_history_ms"]
                    if math.floor(ms * raw_profile["sample_rate_hz"] / 1000) + 1
                    == raw_profile["tap_count"]
                ]
                if (
                    not expected_aliases
                    or list(raw_profile["requested_history_aliases_ms"])
                    != expected_aliases
                ):
                    raise ValueError("MLP History differs from captured selections")
            if (
                not settings["use_robust_refit"]
                and (
                    raw_profile["robust_k"] != 0
                    or raw_profile["initial_fit_rows"] != raw_profile["refit_rows"]
                )
            ) or (
                settings["use_robust_refit"] and not 2 <= raw_profile["robust_k"] <= 32
            ):
                raise ValueError(
                    "Profile fitting provenance differs from original Robust mode"
                )

    @staticmethod
    def source_reference(data: Mapping[str, object]) -> ProjectSourceReference:
        required = {"path", "worksheet", "size_bytes", "sha256"}
        missing = sorted(required - set(data))
        if missing:
            raise ValueError("recording source is missing: " + ", ".join(missing))
        if not isinstance(data["path"], str) or not isinstance(data["worksheet"], str):
            raise ValueError("recording source path and worksheet must be strings")
        if isinstance(data["size_bytes"], bool) or not isinstance(
            data["size_bytes"], int
        ):
            raise ValueError("recording source size must be an integer")
        if not isinstance(data["sha256"], str):
            raise ValueError("recording source SHA-256 must be a string")
        return ProjectSourceReference(
            data["path"],
            data["worksheet"],
            data["size_bytes"],
            data["sha256"],
        )

    def _validate_recording(
        self, recording: Mapping[str, object], identities: set[str], index: int
    ) -> None:
        required = {
            "recording_id",
            "name",
            "source",
            "mapping",
            "sample_rate_hz",
            "robot_speed_mm_s",
            "collision_offset_mm",
            "row_count",
            "annotations",
            "confirmed",
            "interpolated_indices",
        }
        missing = sorted(required - set(recording))
        if missing:
            raise ValueError(f"recordings[{index}] is missing: " + ", ".join(missing))
        identity = str(recording["recording_id"])
        if not identity or identity in identities:
            raise ValueError("recording identities must be non-empty and unique")
        identities.add(identity)
        self.source_reference(self._mapping(recording["source"], "recording source"))
        confirmed = recording["confirmed"]
        if not isinstance(confirmed, bool):
            raise ValueError("recording confirmed state must be boolean")
        inserted = [
            self._integer(value, "interpolation index")
            for value in self._sequence(
                recording["interpolated_indices"], "interpolation indexes"
            )
        ]
        if inserted != sorted(set(inserted)) or any(
            index <= 0
            or index >= self._integer(recording["row_count"], "row count") - 1
            for index in inserted
        ):
            raise ValueError(
                "interpolation indexes must be ordered unique interior sample indexes"
            )
        if not confirmed:
            if recording["mapping"] is not None or recording["annotations"]:
                raise ValueError(
                    "unconfirmed recordings cannot contain mappings or annotations"
                )
            if (
                recording["sample_rate_hz"] is not None
                or recording["robot_speed_mm_s"] is not None
                or recording["collision_offset_mm"] is not None
            ):
                raise ValueError(
                    "unconfirmed recordings cannot contain confirmed test conditions"
                )
            if self._integer(recording["row_count"], "row count") != 0:
                raise ValueError("unconfirmed recordings must have zero loaded rows")
            return
        mapping = self._mapping(recording["mapping"], "recording mapping")
        mapping_required = {
            "data_start_row",
            "header_row",
            "time_column",
            "time_unit",
            "sample_rate_hz",
            "internal_columns",
            "external_columns",
        }
        mapping_missing = sorted(mapping_required - set(mapping))
        if mapping_missing:
            raise ValueError(
                "recording mapping is missing: " + ", ".join(mapping_missing)
            )
        columns = tuple(mapping.get("internal_columns", ())) + tuple(
            mapping.get("external_columns", ())
        )
        if (
            len(columns) != (3 if mapping.get("single_sensor") else 6)
            or len(set(columns)) != (3 if mapping.get("single_sensor") else 6)
            or not all(isinstance(value, str) and value for value in columns)
        ):
            raise ValueError("recording mapping requires six distinct IMU columns")
        if "signal_mapping_schema" in mapping:
            if mapping["signal_mapping_schema"] != 1:
                raise ValueError("Unsupported signal mapping schema")
            signals = self._mapping(mapping.get("signals"), "mapped signals")
            if set(signals) != {"internal", "external"}:
                raise ValueError("Signal mapping requires both sensor descriptors")
            for sensor, descriptor in signals.items():
                descriptor = self._mapping(descriptor, "sensor descriptor")
                mode = descriptor.get("mode")
                raw = self._sequence(descriptor.get("raw_columns"), "raw XYZ")
                filtered = self._sequence(
                    descriptor.get("filtered_columns"), "filtered XYZ"
                )
                if mode not in {"raw", "already_filtered", "application_filtered"}:
                    raise ValueError("Invalid signal source mode")
                for group in (raw, filtered):
                    if group and (
                        len(group) != 3
                        or len(set(group)) != 3
                        or not all(isinstance(v, str) and v for v in group)
                    ):
                        raise ValueError(
                            "Source requires a complete distinct XYZ group"
                        )
                if bool(filtered) != (mode == "already_filtered") or (
                    mode == "application_filtered" and not raw
                ):
                    raise ValueError(
                        "Filtered mapping and software filtering are mutually exclusive"
                    )
                if list(mapping.get(sensor + "_columns", ())) != list(raw or filtered):
                    raise ValueError("Primary columns differ from mapped source")
                processing = descriptor.get("settings")
                if mode != "raw":
                    processing = self._mapping(processing, "filter settings")
                    if (
                        processing.get("sensor") != sensor
                        or processing.get("source_mode") != mode
                    ):
                        raise ValueError("Filter settings differ from source identity")
                    if bool(processing.get("filters")) != (
                        mode == "application_filtered"
                    ):
                        raise ValueError(
                            "Adopted filter design is missing or unexpected"
                        )
                elif processing is not None:
                    raise ValueError("Raw mode cannot contain filter settings")
        elif mapping.get("single_sensor"):
            sensor = mapping["single_sensor"]
            if (
                sensor not in {"internal", "external"}
                or mapping.get("single_imu_schema") != 1
            ):
                raise ValueError("Invalid single-IMU source schema")
            if len(mapping.get(sensor + "_columns", ())) != 3:
                raise ValueError(
                    "Single-IMU source columns do not match sensor identity"
                )
            processing = self._mapping(
                mapping.get("preprocessing"), "single-IMU preprocessing"
            )
            if processing.get("sensor") != sensor or processing.get(
                "source_mode"
            ) not in {"already_filtered", "application_filtered"}:
                raise ValueError("Invalid single-IMU preprocessing identity")
            if self._integer(processing.get("warmup_samples"), "warmup samples") < 1:
                raise ValueError("Warmup samples must be positive")
            stages = self._sequence(processing.get("filters"), "filter stages")
            if bool(stages) != (processing["source_mode"] == "application_filtered"):
                raise ValueError("Filter stages do not match source mode")
        if self._integer(mapping.get("data_start_row"), "Data Start Row") < 1:
            raise ValueError("Data Start Row must be positive")
        header_row = mapping.get("header_row")
        if header_row is not None and self._integer(header_row, "Header Row") < 1:
            raise ValueError("Header Row must be positive")
        time_column = mapping.get("time_column")
        time_unit = mapping.get("time_unit")
        fixed_rate = mapping.get("sample_rate_hz")
        if time_column is None:
            if (
                time_unit is not None
                or self._number(fixed_rate, "fixed Sample Rate") <= 0
            ):
                raise ValueError(
                    "mapping without a Time column requires a positive fixed Sample Rate"
                )
        elif (
            not isinstance(time_column, str)
            or not time_column
            or time_unit not in {"s", "ms", "us", "µs"}
            or fixed_rate is not None
        ):
            raise ValueError(
                "mapping Time column requires a supported Time Unit and no fixed Sample Rate"
            )
        if self._number(recording["sample_rate_hz"], "Sample Rate") <= 0:
            raise ValueError("Sample Rate must be positive")
        if self._number(recording["robot_speed_mm_s"], "Robot Speed") <= 0:
            raise ValueError("Robot Speed must be positive")
        row_count = self._integer(recording["row_count"], "row count")
        if row_count <= 0:
            raise ValueError("row count must be positive")
        interval_ids: set[str] = set()
        for raw in self._sequence(recording["annotations"], "annotations"):
            interval = self._mapping(raw, "annotation")
            annotation_required = {
                "kind",
                "start_index",
                "end_index",
                "reason",
                "provisional",
                "source_recording_id",
                "source_cycle_index",
                "interval_id",
            }
            annotation_missing = sorted(annotation_required - set(interval))
            if annotation_missing:
                raise ValueError(
                    "annotation is missing: " + ", ".join(annotation_missing)
                )
            if interval.get("kind") not in self.ACTIVITY_KINDS:
                raise ValueError("unknown annotation kind")
            start = self._integer(interval.get("start_index"), "annotation start")
            end = self._integer(interval.get("end_index"), "annotation end")
            if start < 0 or end <= start or end > row_count:
                raise ValueError("annotation range is outside its recording")
            interval_id = str(interval.get("interval_id", ""))
            if not interval_id or interval_id in interval_ids:
                raise ValueError(
                    "annotation identities must be non-empty and unique per recording"
                )
            interval_ids.add(interval_id)
            if not isinstance(interval["provisional"], bool):
                raise ValueError("annotation provisional state must be boolean")
            if interval["provisional"]:
                if (
                    not str(interval["source_recording_id"] or "").strip()
                    or interval["source_cycle_index"] is None
                ):
                    raise ValueError(
                        "provisional annotation requires reference provenance"
                    )
                self._integer(interval["source_cycle_index"], "annotation source Cycle")
            elif (
                interval["source_recording_id"] is not None
                or interval["source_cycle_index"] is not None
            ):
                raise ValueError(
                    "confirmed annotation cannot contain proposal provenance"
                )
            if (
                interval.get("kind") == "Ignore"
                and not str(interval.get("reason", "")).strip()
            ):
                raise ValueError("Ignore annotation requires a reason")

    def _validate_results(
        self, results: Mapping[str, object], project: Mapping[str, object]
    ) -> None:
        if results.get("state") != "complete":
            raise ValueError("only completed results may be persisted")
        required_results = {
            "state",
            "profiles",
            "selected_kernel_ids",
            "preview_kernel_id",
        }
        missing_results = sorted(required_results - set(results))
        if missing_results:
            raise ValueError("results are missing: " + ", ".join(missing_results))
        profiles = self._sequence(results.get("profiles"), "result profiles")
        kernel_ids: set[str] = set()
        for raw in profiles:
            profile = self._mapping(raw, "result Profile")
            missing = sorted(self.PROFILE_FIELDS - set(profile))
            if missing:
                raise ValueError("result Profile is missing: " + ", ".join(missing))
            if profile["numeric_type"] not in self.NUMERIC_TYPES - {""}:
                raise ValueError("result Profile has unknown numeric type")
            if profile["numeric_type"] != project["numeric_type"]:
                raise ValueError(
                    "result Profile Target Numeric Type does not match the project"
                )
            if profile["schema_version"] != self.ALGORITHM_CONTRACT:
                raise ValueError("result Profile has incompatible schema")
            kernel_id = str(profile["kernel_id"])
            if not kernel_id or kernel_id in kernel_ids:
                raise ValueError(
                    "result Profile kernel identities must be non-empty and unique"
                )
            kernel_ids.add(kernel_id)
            if not isinstance(profile["qualified"], bool) or not profile["qualified"]:
                raise ValueError("persisted result Profiles must be qualified")
            if self._number(profile["sample_rate_hz"], "Profile Sample Rate") <= 0:
                raise ValueError("Profile Sample Rate must be positive")
            confirmed_rates = {
                float(recording["sample_rate_hz"])
                for recording in project["recordings"]
                if recording["confirmed"]
            }
            if confirmed_rates != {float(profile["sample_rate_hz"])}:
                raise ValueError(
                    "result Profile Sample Rate does not match confirmed recordings"
                )
            tap_count = self._integer(profile["tap_count"], "Profile tap count")
            if tap_count < 1:
                raise ValueError("Profile tap count must be positive")
            family = profile.get("model_family", "fir")
            if family not in {"fir", "mlp", "self_ridge"}:
                raise ValueError("unknown Profile model family")
            if family == "self_ridge":
                if profile.get("model_schema") != 1 or profile.get("lag_start") != 1:
                    raise ValueError("Unsupported self-prediction lag/model schema")
                if "algorithm_runs" not in project and not all(
                    (r.get("mapping") or {}).get("single_sensor")
                    for r in project["recordings"]
                    if r["confirmed"]
                ):
                    raise ValueError(
                        "Self-model requires single-sensor source mappings"
                    )
            if family == "mlp":
                if (
                    profile["cross_validation_evidence_level"]
                    != "BALANCED_COMPLETE_CYCLE_FOLDS"
                ):
                    raise ValueError("MLP requires original fold evidence")
                if profile.get("model_schema") != 1:
                    raise ValueError("unsupported MLP model schema")
                weights = self._sequence(profile["weights"], "MLP weights")
                biases = self._sequence(profile["biases"], "MLP biases")
                if len(weights) < 2 or len(weights) != len(biases):
                    raise ValueError("MLP requires hidden and output affine layers")
                previous = 3 * tap_count
                for index, (matrix, bias) in enumerate(zip(weights, biases)):
                    rows = self._sequence(matrix, "MLP layer weights")
                    width = len(self._sequence(bias, "MLP layer biases"))
                    if width not in (
                        (3,) if index == len(weights) - 1 else (4, 8, 16, 32, 64, 128)
                    ):
                        raise ValueError("invalid MLP layer width")
                    if len(rows) != previous or any(
                        len(self._sequence(row, "MLP weight row")) != width
                        for row in rows
                    ):
                        raise ValueError("MLP layer shape mismatch")
                    for row in rows:
                        for value in row:
                            self._number(value, "MLP weight")
                    for value in bias:
                        self._number(value, "MLP bias")
                    previous = width
                if not 1 <= self._integer(
                    profile.get("mlp_epochs"), "MLP epochs"
                ) <= 200 or profile.get("mlp_stop_reason") not in {
                    "patience",
                    "epoch-cap",
                    "zero-loss",
                }:
                    raise ValueError("invalid MLP training termination")
                if (
                    profile["scale_method"] != "STD"
                    or profile["score_mode"] != "L2_NORM"
                    or profile["robust_k"] != 0
                ):
                    raise ValueError("MLP scoring contract mismatch")
                for field in ("residual_centers", "residual_scales"):
                    if len(self._sequence(profile[field], field)) != 3:
                        raise ValueError("MLP residual parameters require three axes")
                if any(
                    self._number(v, "MLP residual scale") <= 0
                    for v in profile["residual_scales"]
                ):
                    raise ValueError("MLP residual scales must be positive")
            else:
                weights = self._sequence(profile["weights"], "Profile weights")
                if len(weights) != 3 or any(
                    len(self._sequence(row, "Profile weight row")) != 3
                    for row in weights
                ):
                    raise ValueError(
                        "Profile weights must use three output and three input axes"
                    )
                for output in weights:
                    for axis in self._sequence(output, "Profile weight row"):
                        if (
                            len(self._sequence(axis, "Profile weight taps"))
                            != tap_count
                        ):
                            raise ValueError("Profile weight tap count is inconsistent")
                for field in ("biases", "residual_centers", "residual_scales"):
                    if len(self._sequence(profile[field], f"Profile {field}")) != 3:
                        raise ValueError(f"Profile {field} must contain three axes")
            if profile["scale_method"] not in {"STD", "MAD"}:
                raise ValueError("result Profile has unknown residual scale method")
            if profile["score_mode"] not in {"MAX_ABS", "L2_NORM"}:
                raise ValueError("result Profile has unknown score mode")
            if profile["confirmation_mode"] not in {
                "1_OF_1",
                "2_CONSECUTIVE",
                "2_OF_3",
            }:
                raise ValueError("result Profile has unknown confirmation mode")
            if (
                not 1e-6
                <= self._number(profile["ridge_alpha"], "Profile Ridge alpha")
                <= 100
            ):
                raise ValueError("result Profile Ridge alpha is outside [1e-6,100]")
            if self._integer(profile["robust_k"], "Profile robust K") not in (
                set(range(2, 33))
                | (
                    {0}
                    if profile["cross_validation_evidence_level"]
                    == "BALANCED_COMPLETE_CYCLE_FOLDS"
                    else set()
                )
            ):
                raise ValueError(
                    "result Profile robust K is outside the algorithm grid"
                )
            threshold = self._number(profile["threshold"], "Profile threshold")
            if threshold <= 0:
                raise ValueError("result Profile threshold must be positive")
            for field in ("training_speed_range", "qualified_speed_range"):
                speed_range = self._sequence(profile[field], f"Profile {field}")
                if len(speed_range) != 2 or self._number(
                    speed_range[0], field
                ) > self._number(speed_range[1], field):
                    raise ValueError(f"Profile {field} must be an ordered pair")
            if (
                self._number(
                    profile["worst_collision_latency_ms"], "Profile Collision latency"
                )
                > 150
            ):
                raise ValueError("result Profile Collision latency exceeds 150 ms")
            for raw_coverage in self._sequence(profile["coverage"], "Profile coverage"):
                coverage = self._mapping(raw_coverage, "Profile coverage row")
                coverage_missing = sorted(self.COVERAGE_FIELDS - set(coverage))
                if coverage_missing:
                    raise ValueError(
                        "Profile coverage row is missing: "
                        + ", ".join(coverage_missing)
                    )
                if coverage["qualification_status"] not in {
                    "PASS",
                    "FAIL",
                    "OUT_OF_QUALIFIED_RANGE",
                    "COVERAGE_GAP",
                }:
                    raise ValueError(
                        "Profile coverage has unknown qualification status"
                    )
        selected = self._sequence(
            results["selected_kernel_ids"], "selected kernel identities"
        )
        if len(set(selected)) != len(selected):
            raise ValueError("selected kernel identities must be unique")
        if any(
            not isinstance(value, str) or value not in kernel_ids for value in selected
        ):
            raise ValueError(
                "selected kernel identity does not reference a retained Profile"
            )
        preview = results["preview_kernel_id"]
        if not isinstance(preview, str) or (preview and preview not in kernel_ids):
            raise ValueError(
                "preview kernel identity does not reference a retained Profile"
            )

    def _reject_waveform_payload(self, value: object, path: str) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if str(key).lower() in self.FORBIDDEN_WAVEFORM_KEYS:
                    raise ValueError(f"{path} contains a forbidden waveform payload")
                self._reject_waveform_payload(child, f"{path}.{key}")
        elif isinstance(value, Sequence) and not isinstance(
            value, (str, bytes, bytearray)
        ):
            for index, child in enumerate(value):
                self._reject_waveform_payload(child, f"{path}[{index}]")

    def _finite_tree(self, value: object, path: str) -> None:
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"{path} must contain finite numbers only")
        if isinstance(value, Mapping):
            for key, child in value.items():
                if not isinstance(key, str):
                    raise ValueError(f"{path} keys must be strings")
                self._finite_tree(child, f"{path}.{key}")
        elif isinstance(value, Sequence) and not isinstance(
            value, (str, bytes, bytearray)
        ):
            for index, child in enumerate(value):
                self._finite_tree(child, f"{path}[{index}]")
        elif value is not None and not isinstance(value, (str, bool, int, float)):
            raise ValueError(f"{path} contains an unserializable value")

    @staticmethod
    def _mapping(value: object, name: str) -> Mapping[str, object]:
        if not isinstance(value, Mapping):
            raise ValueError(f"{name} must be an object")
        return value

    @staticmethod
    def _sequence(value: object, name: str) -> Sequence[object]:
        if not isinstance(value, Sequence) or isinstance(
            value, (str, bytes, bytearray)
        ):
            raise ValueError(f"{name} must be an array")
        return value

    @staticmethod
    def _integer(value: object, name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{name} must be an integer")
        return value

    @staticmethod
    def _number(value: object, name: str) -> float:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            raise ValueError(f"{name} must be finite")
        return float(value)
