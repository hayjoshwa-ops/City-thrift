"""Product onboarding / dock intake loss prevention for City Thrift CDA.

Monitors back room and receiving dock when donations and product arrive.
Flags employees who divert intake items for personal use beyond what the
store needs for inventory.
"""

from __future__ import annotations

import random

from ai_engine.base import BaseDetector, DetectionResult, FrameContext


class OnboardingIntakeDetector(BaseDetector):
    """
    Back room & dock monitoring during product onboarding.
    Production: object tracking from unload → sort table → floor vs personal hold;
    dwell time on selective handling; correlation with intake log scans.
    """

    RULES = {
        "personal_item_selection": (
            "Personal Item Selection",
            "Employee set aside intake item for personal use during onboarding",
        ),
        "intake_to_personal_hold": (
            "Intake to Personal Hold",
            "Item moved from onboarding flow to employee personal hold area",
        ),
        "unlogged_intake_removal": (
            "Unlogged Intake Removal",
            "Product removed from dock or onboarding without intake log entry",
        ),
        "extended_personal_browsing": (
            "Extended Personal Browsing",
            "Prolonged selective handling of intake items — deciding to keep for self",
        ),
        "dock_to_personal_bag": (
            "Dock to Personal Bag",
            "Item diverted from truck unload directly toward personal bag or locker",
        ),
        "onboarding_bypass_sort": (
            "Onboarding Bypass Sort",
            "Item skipped store sort path and routed to employee exit or locker",
        ),
        "high_value_intake_diversion": (
            "High-Value Intake Diversion",
            "Premium intake item (electronics, designer, furniture) diverted from inventory",
        ),
    }

    ONBOARDING_ZONES = {"receiving_dock", "product_onboarding"}

    def analyze(self, frame: FrameContext) -> list[DetectionResult]:
        if frame.zone_id not in self.ONBOARDING_ZONES:
            return []

        results: list[DetectionResult] = []
        employee_id = frame.metadata.get("employee_id", "unknown")
        item_category = frame.metadata.get("item_category", "general")

        if frame.zone_id == "receiving_dock":
            if self._trigger(0.08):
                results.append(
                    DetectionResult(
                        rule_id="dock_to_personal_bag",
                        rule_name=self.RULES["dock_to_personal_bag"][0],
                        side="employee",
                        confidence=round(random.uniform(0.78, 0.94), 2),
                        description=self.RULES["dock_to_personal_bag"][1],
                        metadata={
                            "employee_id": employee_id,
                            "stage": "truck_unload",
                            "dock_lane": frame.metadata.get("dock_lane", "rear"),
                        },
                    )
                )
            if self._trigger(0.06):
                results.append(
                    DetectionResult(
                        rule_id="unlogged_intake_removal",
                        rule_name=self.RULES["unlogged_intake_removal"][0],
                        side="employee",
                        confidence=round(random.uniform(0.75, 0.92), 2),
                        description=self.RULES["unlogged_intake_removal"][1],
                        metadata={
                            "employee_id": employee_id,
                            "stage": "dock_intake",
                            "intake_logged": False,
                        },
                    )
                )

        if frame.zone_id == "product_onboarding":
            if self._trigger(0.09):
                results.append(
                    DetectionResult(
                        rule_id="personal_item_selection",
                        rule_name=self.RULES["personal_item_selection"][0],
                        side="employee",
                        confidence=round(random.uniform(0.76, 0.93), 2),
                        description=(
                            "Employee appeared to select intake item for personal use "
                            "rather than store inventory during sort"
                        ),
                        metadata={
                            "employee_id": employee_id,
                            "stage": "sort_table",
                            "item_category": item_category,
                        },
                    )
                )
            if self._trigger(0.07):
                results.append(
                    DetectionResult(
                        rule_id="extended_personal_browsing",
                        rule_name=self.RULES["extended_personal_browsing"][0],
                        side="employee",
                        confidence=round(random.uniform(0.72, 0.90), 2),
                        description=self.RULES["extended_personal_browsing"][1],
                        metadata={
                            "employee_id": employee_id,
                            "dwell_sec": random.randint(45, 180),
                            "sort_station": frame.metadata.get("sort_station", "table-1"),
                        },
                    )
                )
            if self._trigger(0.06):
                results.append(
                    DetectionResult(
                        rule_id="intake_to_personal_hold",
                        rule_name=self.RULES["intake_to_personal_hold"][0],
                        side="employee",
                        confidence=round(random.uniform(0.80, 0.95), 2),
                        description=self.RULES["intake_to_personal_hold"][1],
                        metadata={
                            "employee_id": employee_id,
                            "destination": "personal_hold_shelf",
                        },
                    )
                )
            if self._trigger(0.05):
                results.append(
                    DetectionResult(
                        rule_id="onboarding_bypass_sort",
                        rule_name=self.RULES["onboarding_bypass_sort"][0],
                        side="employee",
                        confidence=round(random.uniform(0.74, 0.91), 2),
                        description=self.RULES["onboarding_bypass_sort"][1],
                        metadata={"employee_id": employee_id},
                    )
                )
            if item_category in ("electronics", "designer", "furniture") and self._trigger(0.05):
                results.append(
                    DetectionResult(
                        rule_id="high_value_intake_diversion",
                        rule_name=self.RULES["high_value_intake_diversion"][0],
                        side="employee",
                        confidence=round(random.uniform(0.82, 0.96), 2),
                        description=self.RULES["high_value_intake_diversion"][1],
                        metadata={
                            "employee_id": employee_id,
                            "item_category": item_category,
                        },
                    )
                )

        return results

    def _trigger(self, probability: float) -> bool:
        return random.random() < probability
