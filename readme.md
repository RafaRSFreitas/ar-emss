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

```
ar-project/
├── main.py              # FastAPI app and all routes
├── database.py          # SQLite connection setup
├── models.py            # Fault SQLAlchemy model
├── schemas.py           # Pydantic input/output schemas
├── requirements.txt     # Python dependencies
├── .gitignore
└── static/
    ├── index.html       # Dashboard page
    ├── api.js           # fetch calls to backend
    ├── ui.js            # HTML rendering + escapeHtml
    └── main.js          # event wiring and initialisation
```


## How to run

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
uvicorn main:app --reload

