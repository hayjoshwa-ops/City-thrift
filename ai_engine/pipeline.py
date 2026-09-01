"""AI detection pipeline for City Thrift loss prevention."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from ai_engine.base import FrameContext, results_to_events
from ai_engine.detectors.customer import CustomerLossPreventionDetector
from ai_engine.detectors.employee import EmployeeLossPreventionDetector

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "city_thrift_cda.yaml"


class LossPreventionPipeline:
    def __init__(self) -> None:
        with open(CONFIG_PATH) as f:
            self.config = yaml.safe_load(f)
        self.customer_detector = CustomerLossPreventionDetector()
        self.employee_detector = EmployeeLossPreventionDetector()
        self._zone_map = {z["id"]: z for z in self.config["zones"]}

    def process_frame(
        self,
        camera_id: str,
        *,
        timestamp: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        zone = self._zone_for_camera(camera_id)
        if not zone:
            return []

        frame = FrameContext(
            camera_id=camera_id,
            zone_id=zone["id"],
            zone_name=zone["name"],
            timestamp=timestamp or datetime.now(timezone.utc),
            metadata=metadata or {},
        )

        results = []
        if zone.get("customer_rules"):
            results.extend(self.customer_detector.analyze(frame))
        if zone.get("employee_rules"):
            results.extend(self.employee_detector.analyze(frame))

        return results_to_events(results, frame)

    def _zone_for_camera(self, camera_id: str) -> dict | None:
        for zone in self.config["zones"]:
            if camera_id in zone.get("cameras", []):
                return zone
        return None

    def list_cameras(self) -> list[dict[str, str]]:
        cameras = []
        for zone in self.config["zones"]:
            for cam in zone.get("cameras", []):
                cameras.append(
                    {
                        "camera_id": cam,
                        "zone_id": zone["id"],
                        "zone_name": zone["name"],
                    }
                )
        return cameras
