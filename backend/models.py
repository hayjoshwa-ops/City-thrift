from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AlertTier(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MonitorSide(str, Enum):
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    BOTH = "both"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class DetectionEvent(BaseModel):
    id: str
    timestamp: datetime
    zone_id: str
    zone_name: str
    camera_id: str
    side: MonitorSide
    rule_id: str
    rule_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class Alert(BaseModel):
    id: str
    created_at: datetime
    tier: AlertTier
    side: MonitorSide
    status: AlertStatus = AlertStatus.OPEN
    title: str
    description: str
    zone_id: str
    zone_name: str
    events: list[DetectionEvent] = Field(default_factory=list)
    pos_transaction_id: str | None = None
    employee_id: str | None = None
    clip_url: str | None = None


class Zone(BaseModel):
    id: str
    name: str
    type: str
    risk_level: str
    cameras: list[str]
    customer_rules: list[str | dict[str, Any]] = Field(default_factory=list)
    employee_rules: list[str] = Field(default_factory=list)
    pos_integrated: bool = False


class StoreInfo(BaseModel):
    id: str
    name: str
    address: str
    city: str
    state: str
    zip: str
    phone: str


class DashboardStats(BaseModel):
    open_alerts: int
    critical_alerts: int
    customer_alerts_today: int
    employee_alerts_today: int
    zones_monitored: int
    cameras_online: int


class POSTransaction(BaseModel):
    id: str
    timestamp: datetime
    register_id: str
    employee_id: str
    type: str
    amount: float | None = None
    items_count: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
