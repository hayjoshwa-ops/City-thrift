from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

from backend.models import (
    Alert,
    AlertStatus,
    AlertTier,
    ConnectionsStatus,
    DashboardStats,
    DetectionEvent,
    IntegrationStatus,
    MonitorSide,
    POSTransaction,
    StoreInfo,
    Zone,
)

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "city_thrift_cda.yaml"
CONNECTIONS_PATH = Path(__file__).resolve().parents[1] / "config" / "connections.yaml"
INTAKE_ZONE_IDS = {"receiving_dock", "product_onboarding"}


class EventStore:
    def __init__(self) -> None:
        self.events: list[DetectionEvent] = []
        self.alerts: list[Alert] = []
        self.pos_transactions: list[POSTransaction] = []
        self._config = self._load_config()

    def _load_config(self) -> dict:
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)

    def get_store(self) -> StoreInfo:
        s = self._config["store"]
        return StoreInfo(
            id=s["id"],
            name=s["name"],
            address=s["address"],
            city=s["city"],
            state=s["state"],
            zip=s["zip"],
            phone=s["phone"],
        )

    def get_zones(self) -> list[Zone]:
        zones = []
        for z in self._config["zones"]:
            zones.append(
                Zone(
                    id=z["id"],
                    name=z["name"],
                    type=z["type"],
                    risk_level=z["risk_level"],
                    cameras=z["cameras"],
                    customer_rules=z.get("customer_rules", []),
                    employee_rules=z.get("employee_rules", []),
                    pos_integrated=z.get("pos_integrated", False),
                )
            )
        return zones

    def get_zone(self, zone_id: str) -> Zone | None:
        return next((z for z in self.get_zones() if z.id == zone_id), None)

    def add_event(self, event: DetectionEvent) -> DetectionEvent:
        self.events.append(event)
        return event

    def add_alert(self, alert: Alert) -> Alert:
        self.alerts.insert(0, alert)
        return alert

    def add_pos_transaction(self, txn: POSTransaction) -> POSTransaction:
        self.pos_transactions.append(txn)
        return txn

    def list_alerts(
        self,
        *,
        side: MonitorSide | None = None,
        tier: AlertTier | None = None,
        status: AlertStatus | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        result = self.alerts
        if side and side != MonitorSide.BOTH:
            result = [a for a in result if a.side == side]
        if tier:
            result = [a for a in result if a.tier == tier]
        if status:
            result = [a for a in result if a.status == status]
        return result[:limit]

    def get_alert(self, alert_id: str) -> Alert | None:
        return next((a for a in self.alerts if a.id == alert_id), None)

    def update_alert_status(self, alert_id: str, status: AlertStatus) -> Alert | None:
        alert = self.get_alert(alert_id)
        if alert:
            alert.status = status
        return alert

    def get_stats(self) -> DashboardStats:
        today = datetime.now(timezone.utc).date()
        today_alerts = [
            a for a in self.alerts if a.created_at.date() == today
        ]
        return DashboardStats(
            open_alerts=sum(1 for a in self.alerts if a.status == AlertStatus.OPEN),
            critical_alerts=sum(
                1
                for a in self.alerts
                if a.tier == AlertTier.CRITICAL and a.status == AlertStatus.OPEN
            ),
            customer_alerts_today=sum(
                1 for a in today_alerts if a.side == MonitorSide.CUSTOMER
            ),
            employee_alerts_today=sum(
                1 for a in today_alerts if a.side == MonitorSide.EMPLOYEE
            ),
            intake_alerts_today=sum(
                1 for a in today_alerts if a.zone_id in INTAKE_ZONE_IDS
            ),
            zones_monitored=len(self.get_zones()),
            cameras_online=sum(len(z.cameras) for z in self.get_zones()),
        )

    def get_connections(self) -> ConnectionsStatus:
        with open(CONNECTIONS_PATH) as f:
            cfg = yaml.safe_load(f)

        integrations = []
        all_connected = True
        for key, data in cfg.get("integrations", {}).items():
            status = data.get("status", "pending")
            if status != "connected":
                all_connected = False
            integrations.append(
                IntegrationStatus(
                    name=key,
                    status=status,
                    notes=data.get("notes"),
                    details={k: v for k, v in data.items() if k not in ("status", "notes")},
                )
            )

        mode = cfg.get("mode", "demo")
        if mode == "demo" or not all_connected:
            message = (
                "Demo mode — no cameras or POS connected yet. "
                "Use demo_simulator.py to preview alerts. See docs/BEFORE_YOU_CONNECT.md."
            )
        else:
            message = "Live mode — integrations connected."

        return ConnectionsStatus(
            mode=mode,
            ready_for_live=all_connected and mode == "live",
            message=message,
            integrations=integrations,
        )

    def correlate_pos_with_event(
        self, event: DetectionEvent, window_sec: int = 3
    ) -> POSTransaction | None:
        """Find POS transaction near event time for checkout/exit correlation."""
        event_ts = event.timestamp
        for txn in reversed(self.pos_transactions):
            delta = abs((event_ts - txn.timestamp).total_seconds())
            if delta <= window_sec:
                return txn
        return None


def create_alert_from_event(
    event: DetectionEvent,
    *,
    tier: AlertTier,
    title: str,
    pos_transaction_id: str | None = None,
    employee_id: str | None = None,
) -> Alert:
    return Alert(
        id=str(uuid.uuid4())[:8],
        created_at=datetime.now(timezone.utc),
        tier=tier,
        side=event.side,
        title=title,
        description=event.description,
        zone_id=event.zone_id,
        zone_name=event.zone_name,
        events=[event],
        pos_transaction_id=pos_transaction_id,
        employee_id=employee_id,
        clip_url=f"/clips/{event.camera_id}/{event.id}.mp4",
    )


store = EventStore()
