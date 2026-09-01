#!/usr/bin/env python3
"""Seed City Thrift CDA loss prevention dashboard with demo alerts."""

from __future__ import annotations

import argparse
import random
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_engine.pipeline import LossPreventionPipeline

API_BASE = "http://127.0.0.1:8000/api"


def seed_pos_transactions(client: httpx.Client, count: int = 5) -> None:
    employees = ["EMP-101", "EMP-102", "EMP-103"]
    for i in range(count):
        client.post(
            f"{API_BASE}/pos/transactions",
            json={
                "id": f"TXN-{uuid.uuid4().hex[:6].upper()}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "register_id": "REG-1",
                "employee_id": random.choice(employees),
                "type": random.choice(["sale", "sale", "void", "discount"]),
                "amount": round(random.uniform(5, 85), 2),
                "items_count": random.randint(1, 8),
            },
        )


def run_simulation(*, bursts: int = 8, interval: float = 1.5) -> None:
    pipeline = LossPreventionPipeline()
    cameras = pipeline.list_cameras()

    with httpx.Client(timeout=10) as client:
        health = client.get(f"{API_BASE}/health")
        health.raise_for_status()
        print(f"Connected: {health.json()}")

        seed_pos_transactions(client)

        intake_cameras = [
            c for c in cameras if c["zone_id"] in ("receiving_dock", "product_onboarding")
        ]
        floor_cameras = [c for c in cameras if c not in intake_cameras]

        for i in range(bursts):
            # Bias toward intake zones ~40% to demo dock/onboarding alerts
            cam = (
                random.choice(intake_cameras)
                if intake_cameras and random.random() < 0.4
                else random.choice(floor_cameras or cameras)
            )
            events = pipeline.process_frame(
                cam["camera_id"],
                metadata={
                    "employee_id": f"EMP-{random.randint(101, 105)}",
                    "aisle": random.choice(["A1", "A2", "B3", "Furniture"]),
                    "item_category": random.choice(
                        ["general", "clothing", "electronics", "designer", "furniture"]
                    ),
                    "sort_station": random.choice(["table-1", "table-2", "table-3"]),
                    "dock_lane": "rear",
                },
            )
            for event in events:
                resp = client.post(f"{API_BASE}/events", json=event)
                resp.raise_for_status()
                alert = resp.json()
                side = alert["side"].upper()
                print(f"[{i+1}/{bursts}] {side} · {alert['tier']} · {alert['title']}")
            time.sleep(interval)

        stats = client.get(f"{API_BASE}/stats").json()
        print("\nDashboard stats:", stats)
        print("Open http://127.0.0.1:8000 to view the LP dashboard.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="City Thrift LP demo simulator")
    parser.add_argument("--bursts", type=int, default=8, help="Number of detection bursts")
    parser.add_argument("--interval", type=float, default=1.5, help="Seconds between bursts")
    args = parser.parse_args()
    run_simulation(bursts=args.bursts, interval=args.interval)
