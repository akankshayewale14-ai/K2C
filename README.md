<<<<<<< HEAD
# KABADIWALA2CONNECT

Bengaluru recycling marketplace: list scrap, compare collector and recycler offers, book pickup, and follow lots through processing.

This is a working full-stack app (React + FastAPI + PostgreSQL). Seeded prices and verification records are labeled **DEMO**. They are not live market feeds or government endorsements.

## Run locally

### 1. Database

```bash
docker compose up -d db
```

Copy `.env.example` to `.env`.

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

On first start the API creates tables and seeds demo users.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Demo logins

Password for all seeded users: `DemoPass123!`

| Role | Email |
|---|---|
| Consumer | ananya@kabadiwala.local |
| Collector | ravi@kabadiwala.local |
| Recycler | peenya@kabadiwala.local |
| Business | itpark@kabadiwala.local |
| Admin | admin@kabadiwala.local |

Traceability demo lot: `BLR-EW-2026-00827`

## Tests

```bash
cd backend && pytest
cd frontend && npm test
```

## API

- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
=======
# K2C
Kabadiwala Connect
>>>>>>> b7a4f0a901fd7670b4e24180cfa4fa6b3783f0fa
