"""Customer-side loss prevention detectors for City Thrift CDA."""

from __future__ import annotations

import random

from ai_engine.base import BaseDetector, DetectionResult, FrameContext


class CustomerLossPreventionDetector(BaseDetector):
    """
    Behavior-based customer monitoring (no facial recognition).
    Production: YOLO + pose estimation for concealment, dwell, exit patterns.
    """

    RULES = {
        "concealment_detection": (
            "Concealment Detection",
            "Hand-to-body or bag placement pattern consistent with concealment",
        ),
        "exit_without_bag_check": (
            "Exit Without Purchase",
            "Person exited sales area without register transaction in correlation window",
        ),
        "loitering_threshold": (
            "Extended Loitering",
            "Individual dwelling beyond threshold in high-risk zone",
        ),
        "donation_area_pilferage": (
            "Donation Area Pilferage",
            "Removal of items from unsorted donation zone",
        ),
        "unauthorized_entry": (
            "Unauthorized Zone Entry",
            "Customer entered employee-only zone",
        ),
        "sweep_theft_pattern": (
            "Sweep Theft Pattern",
            "Rapid multi-item handling consistent with organized theft",
        ),
    }

    def analyze(self, frame: FrameContext) -> list[DetectionResult]:
        results: list[DetectionResult] = []
        zone = frame.zone_id

        if zone == "sales_floor" and self._trigger(0.08):
            results.append(
                DetectionResult(
                    rule_id="concealment_detection",
                    rule_name=self.RULES["concealment_detection"][0],
                    side="customer",
                    confidence=round(random.uniform(0.72, 0.94), 2),
                    description=self.RULES["concealment_detection"][1],
                    metadata={"aisle": frame.metadata.get("aisle", "unknown")},
                )
            )

        if zone == "entrance_exit" and self._trigger(0.06):
            results.append(
                DetectionResult(
                    rule_id="exit_without_bag_check",
                    rule_name=self.RULES["exit_without_bag_check"][0],
                    side="customer",
                    confidence=round(random.uniform(0.78, 0.96), 2),
                    description=self.RULES["exit_without_bag_check"][1],
                    metadata={"direction": "exit"},
                )
            )

        if zone == "donation_dropoff" and self._trigger(0.05):
            results.append(
                DetectionResult(
                    rule_id="donation_area_pilferage",
                    rule_name=self.RULES["donation_area_pilferage"][0],
                    side="customer",
                    confidence=round(random.uniform(0.70, 0.90), 2),
                    description=self.RULES["donation_area_pilferage"][1],
                    metadata={"dropoff_lane": "rear"},
                )
            )

        if zone == "back_of_house" and self._trigger(0.04):
            results.append(
                DetectionResult(
                    rule_id="unauthorized_entry",
                    rule_name=self.RULES["unauthorized_entry"][0],
                    side="customer",
                    confidence=round(random.uniform(0.85, 0.98), 2),
                    description=self.RULES["unauthorized_entry"][1],
                    metadata={},
                )
            )

        return results

    def _trigger(self, probability: float) -> bool:
        return random.random() < probability
