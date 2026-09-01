# Before You Connect — City Thrift CDA

You **do not need cameras, POS, or network hardware** to use this project today. It runs in **demo mode** until you are ready.

## What works right now (no connections)

1. Install and run the dashboard locally
2. Preview alert types for customer, employee, and intake/dock monitoring
3. Review zones, rules, and store config for your CDA location
4. Train managers on the LP dashboard using simulated alerts

```bash
pip install -r requirements.txt
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
python3 scripts/demo_simulator.py
```

Open **http://127.0.0.1:8000** on the same computer running the server.

> **Note:** `127.0.0.1` only works on that machine. To view from a phone or another PC on your network, use your computer's local IP (e.g. `http://192.168.1.50:8000`) and start the server with `--host 0.0.0.0`.

Check connection status anytime: **GET /api/connections**

---

## When you are ready to connect

Use this checklist. Nothing here is required to explore the demo.

### 1. Cameras (15 planned zones)

| Priority | Zone | Why |
|----------|------|-----|
| High | Checkout | POS correlation, sweethearting |
| High | Receiving dock | Truck unload, personal diversion |
| High | Product onboarding | Back room sort, personal item selection |
| Medium | Entrance / exit | Exit-without-payment |
| Medium | Donation drop-off | Rear pilferage |
| Medium | Sales floor | Concealment |
| Lower | Office / safe | Cash handling |

**You will need:**
- Existing IP cameras or NVR with RTSP/ONVIF export
- Camera URLs mapped to `cam-01` … `cam-15` in config
- Coverage of dock unload and sort tables (your new intake concern)

### 2. POS / registers

**You will need:**
- POS vendor name (Square, Clover, Lightspeed, etc.)
- Way to send voids, discounts, refunds to the API (`POST /api/pos/transactions`) or a webhook

### 3. On-site hardware (later phase)

- Edge box (NVIDIA Jetson or Intel NUC) on the store LAN
- Optional: monitor at manager desk for live dashboard

### 4. Store policy

- Employee monitoring notice (Idaho / your counsel)
- Rule for employee purchases from intake (manager approval)
- Who receives critical alerts (owner, manager, LP)

---

## Connection config file

Edit `config/connections.yaml` when each piece goes live:

```yaml
mode: demo        # change to "live" when cameras + POS are connected
integrations:
  cameras:
    status: pending   # change to "connected"
  pos:
    status: pending
```

---

## Common “can’t connect” situations

| Situation | What to do |
|-----------|------------|
| Dashboard won't load | Make sure the server is running (`uvicorn` command above) |
| Opening on phone doesn't work | Use your PC's LAN IP, not `127.0.0.1`; use `--host 0.0.0.0` |
| No alerts showing | Run `python3 scripts/demo_simulator.py` in a second terminal |
| Cameras not ready | Stay in demo mode — no action needed yet |
| POS not ready | Checkout rules still preview in demo; live correlation waits for POS |

---

## Suggested rollout (when ready)

1. **Demo & training** — now, no hardware
2. **Checkout + 1–2 cameras** — first live ROI
3. **Dock + back room onboarding** — intake personal-selection monitoring
4. **Remaining zones** — floor, entrance, donation area

Questions to answer before go-live: NVR brand, number of existing cameras, POS system, and whether you want alerts on a store PC only or also on managers' phones.
