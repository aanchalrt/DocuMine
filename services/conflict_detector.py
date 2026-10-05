"""
Conflict detection engine for DocuMine.
Detects numeric variance, categorical changes, sum mismatches, and low-confidence fields
across the corpus of ingested documents.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4


# Month field names used for sum-mismatch checks
_MONTHLY_FIELDS = [
    "monthly_production_jan",
    "monthly_production_feb",
    "monthly_production_mar",
    "monthly_production_apr",
    "monthly_production_may",
    "monthly_production_jun",
    "monthly_production_jul",
    "monthly_production_aug",
    "monthly_production_sep",
    "monthly_production_oct",
    "monthly_production_nov",
    "monthly_production_dec",
]

_NUMERIC_FIELDS = [
    "coal_reserve_mt",
    "annual_production_mt",
    "seam_depth_m",
    "water_discharge_mld",
    "dust_concentration",
    "plantation_area_ha",
]

_CATEGORICAL_FIELDS = ["coal_grade", "estimation_method", "mine_type"]


class ConflictDetector:
    """Detects data conflicts across a list of extracted documents."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_all_conflicts(self, documents: list[dict]) -> list[dict]:
        """
        Run all conflict checks and return a de-duplicated list of conflict dicts.
        """
        if not documents or len(documents) < 1:
            return []

        conflicts: list[dict] = []
        conflicts.extend(self._check_numeric_variance(documents))
        conflicts.extend(self._check_categorical_changes(documents))
        conflicts.extend(self._check_sum_mismatch(documents))
        conflicts.extend(self._check_low_confidence(documents))
        return conflicts

    # ------------------------------------------------------------------
    # Check: numeric variance
    # ------------------------------------------------------------------

    def _check_numeric_variance(self, documents: list[dict]) -> list[dict]:
        """
        Flag fields where the same numeric metric differs by > 2% across documents.
        Severity: > 10% → high, 2–10% → medium.
        """
        conflicts: list[dict] = []

        for field_name in _NUMERIC_FIELDS:
            # Collect (doc_id, doc_name, numeric_value) triples
            entries: list[dict] = []
            estimation_methods: dict[str, str] = {}

            for doc in documents:
                fields = doc.get("fields") or []
                for f in fields:
                    if f.get("name") == field_name:
                        try:
                            val = float(f["value"])
                        except (TypeError, ValueError):
                            continue
                        entries.append(
                            {
                                "doc_id": doc.get("id", ""),
                                "doc_name": doc.get("filename", ""),
                                "value": val,
                            }
                        )
                    if f.get("name") == "estimation_method":
                        estimation_methods[doc.get("id", "")] = f.get("value", "")

            if len(entries) < 2:
                continue

            values = [e["value"] for e in entries]
            min_val = min(values)
            max_val = max(values)

            if min_val == 0:
                continue  # Avoid division by zero

            pct_diff = abs(max_val - min_val) / abs(min_val) * 100

            if pct_diff <= 2.0:
                continue

            severity = "high" if pct_diff > 10.0 else "medium"

            # Check whether estimation_method also changed between docs
            unique_methods = set(estimation_methods.values()) - {""}
            note = (
                f"Values differ by {pct_diff:.1f}% across documents. "
            )
            if len(unique_methods) > 1:
                note += (
                    f"Estimation method also changes: {', '.join(unique_methods)}. "
                    "This may explain the variance."
                )
                # Override conflict_type to method_change if method changed
                conflict_type: str = "method_change"
            else:
                conflict_type = "unexplained_variance"

            conflicts.append(
                self._build_conflict(
                    parameter=field_name,
                    conflict_type=conflict_type,
                    severity=severity,
                    values=[
                        {"doc_id": e["doc_id"], "doc_name": e["doc_name"], "value": str(e["value"])}
                        for e in entries
                    ],
                    note=note,
                )
            )

        return conflicts

    # ------------------------------------------------------------------
    # Check: categorical changes
    # ------------------------------------------------------------------

    def _check_categorical_changes(self, documents: list[dict]) -> list[dict]:
        """
        Flag categorical fields that change value across documents.
        coal_grade change → high; others → medium.
        """
        conflicts: list[dict] = []

        for field_name in _CATEGORICAL_FIELDS:
            entries: list[dict] = []

            for doc in documents:
                fields = doc.get("fields") or []
                for f in fields:
                    if f.get("name") == field_name and f.get("value"):
                        entries.append(
                            {
                                "doc_id": doc.get("id", ""),
                                "doc_name": doc.get("filename", ""),
                                "value": str(f["value"]).strip().lower(),
                            }
                        )

            if len(entries) < 2:
                continue

            unique_values = {e["value"] for e in entries}
            if len(unique_values) <= 1:
                continue

            severity = "high" if field_name == "coal_grade" else "medium"
            note = (
                f"Field '{field_name}' takes different values across documents: "
                f"{', '.join(unique_values)}. This may indicate reclassification or error."
            )

            conflicts.append(
                self._build_conflict(
                    parameter=field_name,
                    conflict_type="method_change",
                    severity=severity,
                    values=[
                        {"doc_id": e["doc_id"], "doc_name": e["doc_name"], "value": e["value"]}
                        for e in entries
                    ],
                    note=note,
                )
            )

        return conflicts

    # ------------------------------------------------------------------
    # Check: sum mismatch
    # ------------------------------------------------------------------

    def _check_sum_mismatch(self, documents: list[dict]) -> list[dict]:
        """
        Verify that the sum of monthly production fields equals annual_production_mt
        within a 1% tolerance.
        """
        conflicts: list[dict] = []

        # Find annual production
        annual_entries: list[dict] = []
        for doc in documents:
            for f in doc.get("fields") or []:
                if f.get("name") == "annual_production_mt":
                    try:
                        annual_entries.append(
                            {
                                "doc_id": doc.get("id", ""),
                                "doc_name": doc.get("filename", ""),
                                "value": float(f["value"]),
                            }
                        )
                    except (TypeError, ValueError):
                        pass

        if not annual_entries:
            return []

        # Find monthly production values (may be in a different document)
        for doc in documents:
            monthly_values: dict[str, float] = {}
            for f in doc.get("fields") or []:
                if f.get("name") in _MONTHLY_FIELDS:
                    try:
                        monthly_values[f["name"]] = float(f["value"])
                    except (TypeError, ValueError):
                        pass

            if len(monthly_values) < 3:
                # Not enough monthly data to form a meaningful check
                continue

            monthly_sum = sum(monthly_values.values())

            for annual_entry in annual_entries:
                annual_val = annual_entry["value"]
                if annual_val == 0:
                    continue

                diff_pct = abs(monthly_sum - annual_val) / abs(annual_val) * 100
                if diff_pct > 1.0:
                    conflicts.append(
                        self._build_conflict(
                            parameter="annual_production_mt",
                            conflict_type="sum_mismatch",
                            severity="medium",
                            values=[
                                {
                                    "doc_id": annual_entry["doc_id"],
                                    "doc_name": annual_entry["doc_name"],
                                    "value": f"Annual: {annual_val}",
                                },
                                {
                                    "doc_id": doc.get("id", ""),
                                    "doc_name": doc.get("filename", ""),
                                    "value": f"Monthly sum: {monthly_sum:.3f}",
                                },
                            ],
                            note=(
                                f"Sum of monthly production ({monthly_sum:.3f} Mt) "
                                f"differs from stated annual production ({annual_val} Mt) "
                                f"by {diff_pct:.1f}%."
                            ),
                        )
                    )

        return conflicts

    # ------------------------------------------------------------------
    # Check: low confidence
    # ------------------------------------------------------------------

    def _check_low_confidence(self, documents: list[dict]) -> list[dict]:
        """
        Create a low-severity conflict entry for every field with confidence < 0.6.
        """
        conflicts: list[dict] = []

        for doc in documents:
            doc_id = doc.get("id", "")
            doc_name = doc.get("filename", "")
            for f in doc.get("fields") or []:
                try:
                    confidence = float(f.get("confidence", 1.0))
                except (TypeError, ValueError):
                    confidence = 1.0

                if confidence < 0.6:
                    conflicts.append(
                        self._build_conflict(
                            parameter=f.get("name", "unknown"),
                            conflict_type="low_confidence",
                            severity="low",
                            values=[
                                {
                                    "doc_id": doc_id,
                                    "doc_name": doc_name,
                                    "value": str(f.get("value", "")),
                                }
                            ],
                            note=(
                                f"Field '{f.get('name')}' in document '{doc_name}' "
                                f"has low AI extraction confidence ({confidence:.2f}). "
                                "Manual review recommended."
                            ),
                        )
                    )

        return conflicts

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @staticmethod
    def _build_conflict(
        *,
        parameter: str,
        conflict_type: str,
        severity: str,
        values: list[dict],
        note: str,
    ) -> dict:
        return {
            "id": str(uuid4()),
            "parameter": parameter,
            "conflict_type": conflict_type,
            "severity": severity,
            "values": values,
            "note": note,
            "detected_at": datetime.utcnow().isoformat(),
        }
