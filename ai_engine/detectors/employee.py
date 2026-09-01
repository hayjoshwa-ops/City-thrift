"""Employee-side loss prevention detectors for City Thrift CDA."""

from __future__ import annotations

import random

from ai_engine.base import BaseDetector, DetectionResult, FrameContext


class EmployeeLossPreventionDetector(BaseDetector):
    """
    Employee monitoring via video zones + POS exception correlation.
    Production: POS webhook integration, register overlay analytics.
    """

    RULES = {
        "void_without_customer": (
            "Void Without Customer",
            "Register void with no customer at counter",
        ),
        "excessive_discount": (
            "Excessive Discount",
            "Discount exceeds policy threshold without manager override",
        ),
        "no_sale_drawer_open": (
            "No-Sale Drawer Open",
            "Cash drawer opened outside completed transaction",
        ),
        "sweethearting_pattern": (
            "Sweethearting Pattern",
            "Scan avoidance correlated with customer interaction",
        ),
        "inventory_to_personal_area": (
            "Inventory to Personal Area",
            "Employee moving merchandise toward personal bag/exit path",
        ),
        "solo_cash_count": (
            "Solo Cash Count",
            "Cash handling without dual-control policy",
        ),
        "unsorted_donation_removal": (
            "Unsorted Donation Removal",
            "Employee removing items from donation intake before sorting",
        ),
        "manual_price_override": (
            "Manual Price Override",
            "Manual PLU entry on high-value item",
        ),
    }

    def analyze(self, frame: FrameContext) -> list[DetectionResult]:
        results: list[DetectionResult] = []
        zone = frame.zone_id
        employee_id = frame.metadata.get("employee_id", "unknown")

        if zone == "checkout":
            if self._trigger(0.07):
                results.append(
                    DetectionResult(
                        rule_id="void_without_customer",
                        rule_name=self.RULES["void_without_customer"][0],
                        side="employee",
                        confidence=round(random.uniform(0.80, 0.95), 2),
                        description=self.RULES["void_without_customer"][1],
                        metadata={"employee_id": employee_id, "register": "REG-1"},
                    )
                )
            if self._trigger(0.05):
                results.append(
                    DetectionResult(
                        rule_id="sweethearting_pattern",
                        rule_name=self.RULES["sweethearting_pattern"][0],
                        side="employee",
                        confidence=round(random.uniform(0.75, 0.92), 2),
                        description=self.RULES["sweethearting_pattern"][1],
                        metadata={"employee_id": employee_id},
                    )
                )
            if self._trigger(0.04):
                results.append(
                    DetectionResult(
                        rule_id="excessive_discount",
                        rule_name=self.RULES["excessive_discount"][0],
                        side="employee",
                        confidence=round(random.uniform(0.78, 0.93), 2),
                        description=self.RULES["excessive_discount"][1],
                        metadata={
                            "employee_id": employee_id,
                            "discount_percent": random.randint(51, 80),
                        },
                    )
                )

        if zone == "back_of_house" and self._trigger(0.06):
            results.append(
                DetectionResult(
                    rule_id="inventory_to_personal_area",
                    rule_name=self.RULES["inventory_to_personal_area"][0],
                    side="employee",
                    confidence=round(random.uniform(0.72, 0.91), 2),
                    description=self.RULES["inventory_to_personal_area"][1],
                    metadata={"employee_id": employee_id},
                )
            )

        if zone == "office_safe" and self._trigger(0.03):
            results.append(
                DetectionResult(
                    rule_id="solo_cash_count",
                    rule_name=self.RULES["solo_cash_count"][0],
                    side="employee",
                    confidence=round(random.uniform(0.88, 0.97), 2),
                    description=self.RULES["solo_cash_count"][1],
                    metadata={"employee_id": employee_id},
                )
            )

        if zone == "donation_dropoff" and self._trigger(0.04):
            results.append(
                DetectionResult(
                    rule_id="unsorted_donation_removal",
                    rule_name=self.RULES["unsorted_donation_removal"][0],
                    side="employee",
                    confidence=round(random.uniform(0.70, 0.88), 2),
                    description=self.RULES["unsorted_donation_removal"][1],
                    metadata={"employee_id": employee_id},
                )
            )

        return results

    def _trigger(self, probability: float) -> bool:
        return random.random() < probability
