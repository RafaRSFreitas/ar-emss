# AR Enhanced Maintenance Support System for High-Security Engineering Environments

## What's working right now

- **Backend** runs with FastAPI + SQLite
- **Database** has a `faults` table (title, location, severity, status)
- **API endpoints** live and tested at `/docs`:
  - `GET /api/faults` → list all faults
  - `POST /api/faults` → report a new fault
  - `GET /api/faults/{id}` → single fault
  - `PATCH /api/faults/{id}` → update status (open/closed)
  - `GET /health` → server health check
- **Dashboard** frontend at `/` shows a form to report faults and a live list
- **Static files** served from the `static/` folder (JS modules split as `api.js`, `ui.js`, `main.js`)

## Project structure

ar-project/
├── main.py # FastAPI app, routes, fault CRUD
├── database.py # SQLite connection (maintenance.db)
├── models.py # SQLAlchemy Fault model
├── schemas.py # Pydantic schemas for input/output
├── requirements.txt # Python dependencies
├── static/
│ ├── index.html # Dashboard page
│ ├── api.js # fetch calls to backend
│ ├── ui.js # HTML rendering + XSS escape
│ └── main.js # wires form and refresh
└── maintenance.db # auto-generated database file


## How to run

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload

