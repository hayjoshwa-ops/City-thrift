# City Thrift — AI Loss Prevention Monitoring

AI-integrated security monitoring for **loss prevention** at **City Thrift**, 165 East Appleway Avenue, Coeur d'Alene (CDA), ID. Covers both **customer-side** and **employee-side** threats through behavior-based video analytics and POS correlation.

## What this system monitors

### Customer side
- Concealment and shoplifting patterns on the sales floor
- Exit without matching POS transaction
- Donation drop-off pilferage (rear entrance)
- Unauthorized entry into employee-only areas
- Loitering and organized retail crime recon patterns

### Employee side
- POS voids, no-sales, and excessive discounts
- Sweethearting / scan avoidance at checkout
- Back-of-house inventory movement toward personal areas
- Solo cash handling violations
- Unsorted donation removal before intake processing
- **Back room & dock onboarding** — personal item selection during intake, items diverted to personal hold, unlogged removals from dock/sort

### Intake / dock monitoring
When donations and product arrive at the rear dock and back room sort tables, the system watches employees for:
- Keeping intake items for personal use beyond what the store needs
- Diverting items from truck unload to personal bag or locker
- Extended browsing/sorting behavior indicating personal selection
- High-value items (electronics, designer, furniture) removed from inventory path

## Quick start

```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open **http://127.0.0.1:8000** for the LP dashboard.

Seed demo alerts:

```bash
pip install httpx
python scripts/demo_simulator.py
```

## Project structure

| Path | Purpose |
|------|---------|
| `config/city_thrift_cda.yaml` | Store zones, cameras, alert rules for CDA location |
| `docs/ARCHITECTURE.md` | System design and deployment phases |
| `backend/` | FastAPI REST + WebSocket API |
| `ai_engine/` | Customer & employee detection pipeline |
| `frontend/` | Manager/LP monitoring dashboard |
| `scripts/demo_simulator.py` | Demo event generator |

## API

- `GET /api/health` — Service health
- `GET /api/store` — City Thrift CDA store info
- `GET /api/zones` — Monitored zones and cameras
- `GET /api/alerts` — List alerts (`?side=customer|employee`)
- `POST /api/events` — Ingest AI detection event → creates alert
- `POST /api/pos/transactions` — POS feed for checkout correlation
- `WS /api/ws/alerts` — Real-time alert stream

## Deployment notes (City Thrift CDA)

1. **Phase 1**: Checkout cameras + POS integration (highest shrink ROI)
2. **Phase 2**: Entrance/exit + donation drop-off (Mon–Sat 10–6, Sun 11–6)
3. **Phase 3**: Full sales floor analytics
4. **Phase 4**: Back-of-house employee zones
5. **Phase 5**: Receiving dock + product onboarding (personal intake selection)

Replace demo detectors in `ai_engine/detectors/` with production models (YOLO + pose, POS webhooks). Behavior-only detection — no facial recognition.

## Store reference

- **Address**: 165 East Appleway Avenue, CDA, ID 83814
- **Phone**: 208-268-8600
- **Hours**: Mon–Sat 10–7, Sun 11–7
- **Mission**: Net proceeds support [Wishing Star Foundation](https://www.citythriftshop.com/)
