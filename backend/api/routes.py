from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

from backend.models import (
    Alert,
    AlertStatus,
    AlertTier,
    ConnectionsStatus,
    DashboardStats,
    DetectionEvent,
    MonitorSide,
    POSTransaction,
    StoreInfo,
    Zone,
)
from backend.store import create_alert_from_event, store

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws)


ws_manager = ConnectionManager()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "store": "city-thrift-cda"}


@router.get("/connections", response_model=ConnectionsStatus)
def get_connections() -> ConnectionsStatus:
    return store.get_connections()


@router.get("/store", response_model=StoreInfo)
def get_store() -> StoreInfo:
    return store.get_store()


@router.get("/zones", response_model=list[Zone])
def list_zones() -> list[Zone]:
    return store.get_zones()


@router.get("/zones/{zone_id}", response_model=Zone)
def get_zone(zone_id: str) -> Zone:
    zone = store.get_zone(zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.get("/stats", response_model=DashboardStats)
def get_stats() -> DashboardStats:
    return store.get_stats()


@router.get("/alerts", response_model=list[Alert])
def list_alerts(
    side: MonitorSide | None = None,
    tier: AlertTier | None = None,
    status: AlertStatus | None = None,
    limit: int = Query(default=50, le=200),
) -> list[Alert]:
    return store.list_alerts(side=side, tier=tier, status=status, limit=limit)


@router.get("/alerts/{alert_id}", response_model=Alert)
def get_alert(alert_id: str) -> Alert:
    alert = store.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/alerts/{alert_id}/status", response_model=Alert)
async def update_alert_status(alert_id: str, status: AlertStatus) -> Alert:
    alert = store.update_alert_status(alert_id, status)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    await ws_manager.broadcast({"type": "alert_updated", "alert": alert.model_dump(mode="json")})
    return alert


@router.get("/events", response_model=list[DetectionEvent])
def list_events(limit: int = Query(default=50, le=200)) -> list[DetectionEvent]:
    return store.events[:limit]


@router.post("/events", response_model=Alert)
async def ingest_event(event: DetectionEvent) -> Alert:
    store.add_event(event)
    txn = store.correlate_pos_with_event(event)
    tier = _tier_for_rule(event.rule_id)
    title = _title_for_event(event)
    alert = store.add_alert(
        create_alert_from_event(
            event,
            tier=tier,
            title=title,
            pos_transaction_id=txn.id if txn else None,
            employee_id=txn.employee_id if txn else event.metadata.get("employee_id"),
        )
    )
    await ws_manager.broadcast({"type": "new_alert", "alert": alert.model_dump(mode="json")})
    return alert


@router.post("/pos/transactions", response_model=POSTransaction)
def ingest_pos_transaction(txn: POSTransaction) -> POSTransaction:
    return store.add_pos_transaction(txn)


@router.get("/pos/transactions", response_model=list[POSTransaction])
def list_pos_transactions(limit: int = Query(default=50, le=200)) -> list[POSTransaction]:
    return store.pos_transactions[-limit:]


@router.websocket("/ws/alerts")
async def alerts_websocket(websocket: WebSocket) -> None:
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


def _tier_for_rule(rule_id: str) -> AlertTier:
    critical = {
        "exit_without_bag_check",
        "unpaid_item_exit_correlation",
        "void_without_customer",
        "no_sale_drawer_open",
        "unauthorized_boh_entry",
        "solo_cash_count",
        "donation_area_pilferage",
        "dock_to_personal_bag",
        "high_value_intake_diversion",
    }
    high = {
        "concealment_detection",
        "sweethearting_pattern",
        "excessive_discount",
        "inventory_to_personal_area",
        "unsorted_donation_removal",
        "personal_item_selection",
        "intake_to_personal_hold",
        "unlogged_intake_removal",
        "extended_personal_browsing",
        "onboarding_bypass_sort",
    }
    medium = {
        "loitering_threshold",
        "high_value_area_dwell",
        "discount_pattern_anomaly",
        "manual_price_override",
    }
    if rule_id in critical:
        return AlertTier.CRITICAL
    if rule_id in high:
        return AlertTier.HIGH
    if rule_id in medium:
        return AlertTier.MEDIUM
    return AlertTier.LOW


def _title_for_event(event: DetectionEvent) -> str:
    titles = {
        "concealment_detection": "Possible concealment on sales floor",
        "exit_without_bag_check": "Exit without purchase correlation",
        "unpaid_item_exit_correlation": "Customer exit — no matching POS transaction",
        "void_without_customer": "Void transaction with no customer present",
        "excessive_discount": "Excessive discount applied at register",
        "no_sale_drawer_open": "Cash drawer opened outside sale",
        "sweethearting_pattern": "Possible sweethearting at checkout",
        "unauthorized_boh_entry": "Unauthorized entry — back of house",
        "donation_area_pilferage": "Suspicious activity at donation drop-off",
        "inventory_to_personal_area": "Merchandise moved toward personal area",
        "solo_cash_count": "Solo cash handling violation",
        "loitering_threshold": "Extended loitering in monitored zone",
        "personal_item_selection": "Employee kept intake item for personal use",
        "intake_to_personal_hold": "Intake item moved to personal hold area",
        "unlogged_intake_removal": "Product removed from dock without intake log",
        "extended_personal_browsing": "Employee browsing intake items for personal keep",
        "dock_to_personal_bag": "Item diverted from dock to personal bag",
        "onboarding_bypass_sort": "Intake item bypassed store sort path",
        "high_value_intake_diversion": "High-value intake item diverted from inventory",
    }
    return titles.get(event.rule_id, event.rule_name)
