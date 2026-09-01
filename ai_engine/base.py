from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class FrameContext:
    camera_id: str
    zone_id: str
    zone_name: str
    timestamp: datetime
    metadata: dict[str, Any]


@dataclass
class DetectionResult:
    rule_id: str
    rule_name: str
    side: str
    confidence: float
    description: str
    metadata: dict[str, Any]


class BaseDetector(ABC):
    @abstractmethod
    def analyze(self, frame: FrameContext) -> list[DetectionResult]:
        pass


def results_to_events(
    results: list[DetectionResult], frame: FrameContext
) -> list[dict[str, Any]]:
    events = []
    for r in results:
        events.append(
            {
                "id": str(uuid.uuid4())[:8],
                "timestamp": frame.timestamp.isoformat(),
                "zone_id": frame.zone_id,
                "zone_name": frame.zone_name,
                "camera_id": frame.camera_id,
                "side": r.side,
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "confidence": r.confidence,
                "description": r.description,
                "metadata": {**frame.metadata, **r.metadata},
            }
        )
    return events
