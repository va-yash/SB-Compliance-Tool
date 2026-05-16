# SB Compliance Tool — A320 Fleet Demo

A web-based Service Bulletin compliance management tool for small airline operators.
Tracks SB applicability, accomplishment status, and recurring task due dates across a 10-aircraft A320-214 fleet.

---

## Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python 3.11+ · FastAPI · SQLAlchemy |
| Database | SQLite (file: `backend/sbtrack.db`) |
| Frontend | React 18 · Vite · plain CSS         |
| AI       | Claude claude-sonnet-4-20250514 (Anthropic) |

---

## Setup

### 1. Clone / unzip the project

```bash
cd sb-compliance-tool
```

### 2. Configure your API key

```bash
cp .env.example backend/.env
# Edit backend/.env and add your ANTHROPIC_API_KEY
```

### 3. Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Seed the database

```bash
# Still in backend/
python seed.py
```

Expected output:
```
Database cleared.
  ✓ MSN 0834  F-FAKE1  (Air Occitanie)
  ...
Seed complete.  Aircraft: 10  SB records: 200
```

### 5. Start the backend

```bash
# Still in backend/
uvicorn main:app --reload
```

API now running at http://localhost:8000
Interactive docs at http://localhost:8000/docs

### 6. Install and start the frontend

```bash
cd ../frontend
npm install
npm run dev
```

App now running at http://localhost:5173

---

## Re-seeding

If you want to reset all demo data:

```bash
cd backend
python seed.py
```

This clears all tables and re-populates from scratch. Your `sbtrack.db` file holds all data — delete it to start completely fresh.

---

## Features

### Fleet Overview (`/`)
- 10 A320-214 aircraft across 5 operators
- Traffic light per aircraft: 🔴 AD open · 🟡 open SBs or due soon · 🟢 compliant
- Click any row to go to MSN detail

### MSN Detail (`/aircraft/<msn>`)
**Configuration tab**
- All installed components (engines, APU, landing gear, 6 avionics LRUs)
- Edit any component's PN/SN/software PN — changes are logged
- Full modification history with add/delete

**SB Status Board tab**
- 20 SBs per aircraft, filterable by status / category / ATA / AD / due soon
- Due-soon rows highlighted amber (within 30 days / 50 FH / 50 FC)
- Add, edit, and delete SB records with full conditional form
- CSV export of the complete SB list

### SB Applicability Checker (`/applicability`)
- Upload a Service Bulletin PDF **or** paste effectivity text
- Claude extracts: MSN range, excluded MSNs, required mods, confidence level
- Per-MSN applicability compared against registered fleet
- Collapsible raw JSON output for transparency
- Disclaimer: AI output is indicative, always verify with source document

---

## Project structure

```
sb-compliance-tool/
├── backend/
│   ├── main.py          FastAPI app, CORS, router registration
│   ├── database.py      SQLAlchemy SQLite setup
│   ├── models.py        Aircraft, Component, Modification, SBRecord models
│   ├── schemas.py       Pydantic v2 request/response schemas
│   ├── seed.py          Demo data (10 aircraft, 200 SBs, 6 due-soon scenarios)
│   ├── requirements.txt
│   └── routers/
│       ├── aircraft.py  Fleet + component + modification endpoints
│       └── sb.py        SB CRUD + Claude applicability parser
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js       All fetch calls
│   │   ├── pages/
│   │   │   ├── FleetOverview.jsx
│   │   │   ├── MSNDetail.jsx
│   │   │   └── ApplicabilityChecker.jsx
│   │   ├── components/
│   │   │   ├── Nav.jsx
│   │   │   └── Modal.jsx
│   │   └── styles/main.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js   Proxies /api → localhost:8000
├── .env.example
└── README.md
```

---

## Demo data highlights

| MSN  | Registration | Operator        |  FH    | Due-Soon scenario |
|------|--------------|-----------------|--------|-------------------|
| 0834 | F-FAKE1      | Air Occitanie   | 46,832 | A320-71-2456 in 35 FH |
| 0921 | F-FAKE2      | Air Occitanie   | 43,210 | A320-53-2341 in 22 FH |
| 1205 | OE-LKA       | Alpine Express  | 38,450 | A320-32-1456 in 28 FC |
| 2341 | YU-APB       | Balkan Regional | 27,890 | A320-32-1678 in 18 days |
| 3102 | D-AXRA       | Rhein Air       | 20,150 | A320-57-0678 in 40 FH |
| 4401 | C-FAKE3      | Air Nordique    | 11,890 | A320-71-2234 in 45 FH |

---

## Migrating to PostgreSQL

1. `pip install psycopg2-binary`
2. In `backend/database.py`, replace the `DATABASE_URL` with your Postgres URL:
   ```python
   DATABASE_URL = "postgresql://user:password@localhost/sbtrack"
   ```
3. Remove `connect_args={"check_same_thread": False}` from `create_engine()`
4. Re-run `python seed.py`
