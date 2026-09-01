# City Thrift CDA — AI Loss Prevention Architecture

AI-integrated security monitoring for **City Thrift** at 165 East Appleway Avenue, Coeur d'Alene, ID. The system covers **customer-side** and **employee-side** loss prevention through behavior-based video analytics correlated with POS data.

## Goals

| Side | Primary threats | AI approach |
|------|-----------------|-------------|
| **Customer** | Shoplifting, concealment, donation-area pilferage, organized retail crime recon | Computer vision: loitering, concealment gestures, exit-without-payment correlation |
| **Employee** | Sweethearting, void/discount abuse, back-of-house theft, cash handling fraud, **personal intake selection at dock/onboarding** | POS exception reporting + video correlation, restricted-zone access, behavioral patterns, intake flow tracking |

## System layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    LP Dashboard (Web UI)                        │
│         Alerts · Zone map · Incident review · Reports           │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST + WebSocket
┌────────────────────────────▼────────────────────────────────────┐
│                    Backend API (FastAPI)                        │
│    Events · Alerts · Zones · POS correlation · Audit log        │
└──────┬──────────────────────────────┬───────────────────────────┘
       │                              │
┌──────▼──────────┐            ┌──────▼──────────┐
│  AI Engine      │            │  POS Adapter    │
│  Customer det.  │            │  Voids/discounts│
│  Employee det.  │            │  Refunds/scans  │
└──────┬──────────┘            └─────────────────┘
       │
┌──────▼──────────────────────────────────────────┐
│  Camera feeds (RTSP / ONVIF / existing NVR)     │
│  Zones: entrance, floor, checkout, BOH, donate, dock, onboarding │
└─────────────────────────────────────────────────┘
```

## Customer-side monitoring

1. **Concealment detection** — Hand-to-body / bag placement patterns on sales floor and near exits.
2. **Loitering & dwell** — Extended time in high-shrink areas without purchase intent signals.
3. **Exit correlation** — Person at exit matched to POS: no transaction within correlation window.
4. **Donation area** — After-hours motion, removal of unsorted donations from drop-off zone.
5. **Sweep / ORC patterns** — Group formation, rapid multi-item handling.

Alerts are **behavior-based** (no facial recognition) to reduce privacy and legal risk.

## Employee-side monitoring

1. **POS exceptions** — Voids, no-sales, excessive discounts, manual overrides, refunds without return.
2. **Sweethearting** — Scan avoidance correlated with known register + customer interaction patterns.
3. **Back-of-house** — Customer in employee-only zones; employee removing inventory toward personal areas.
4. **Cash handling** — Solo safe access, drawer open outside transaction context.
5. **Shift correlation** — Anomaly spikes tied to register + employee ID from POS.

## Back room & dock — product onboarding

City Thrift receives donations via rear dock and drop-off. Employees sort intake in the back room before items reach the sales floor. This is a high-shrink stage when staff decide whether to keep items for themselves.

1. **Receiving dock** — Truck unload; flags items diverted to personal bag/locker before intake log.
2. **Product onboarding (sort tables)** — Watches employees during sort for personal selection beyond store needs.
3. **Personal item selection** — Item set aside during sort for employee personal use (not routed to floor/discard).
4. **Extended personal browsing** — Prolonged selective handling — employee deciding if they want an item.
5. **Intake to personal hold** — Item moved to locker, under-table, or exit path instead of inventory.
6. **Unlogged intake removal** — Product leaves dock/onboarding without intake log entry.
7. **High-value diversion** — Electronics, designer, furniture diverted from inventory path.

**Policy** (see `config/city_thrift_cda.yaml` → `intake_policy`): employees cannot remove intake for personal use without manager approval; all items follow **dock → sort → floor/discard**.

## Alert workflow

```
Detection → Tier assignment (critical/high/medium/low)
         → Deduplication & cooldown
         → Dashboard + optional SMS/email to manager
         → Clip saved (30-day retention, bystanders blurred)
         → Manager feedback improves rule thresholds
```

## Deployment at City Thrift CDA

| Phase | Scope |
|-------|--------|
| 1 | Checkout cameras + POS correlation (highest ROI) |
| 2 | Entrance/exit + donation drop-off |
| 3 | Sales floor behavior analytics |
| 4 | Back-of-house employee zones |
| 5 | **Receiving dock + product onboarding** (personal intake selection) |

**Hardware**: Existing IP cameras or Axis/Hikvision equivalents; edge box (NVIDIA Jetson or Intel NUC) on-site; optional cloud backup for clips.

## Repository layout

- `config/city_thrift_cda.yaml` — Store zones, cameras, rules
- `backend/` — REST API and event store
- `ai_engine/` — Customer, employee, and onboarding intake detectors + pipeline
- `frontend/` — LP monitoring dashboard
- `scripts/demo_simulator.py` — Generates sample alerts for demo/training

## Privacy & compliance

- No biometric face matching; behavior and zone rules only.
- 30-day video retention (configurable).
- Role-based dashboard access (manager vs LP vs owner).
- Idaho-focused: align with store policy and counsel for employee monitoring notice.
