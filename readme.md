# AR Enhanced Maintenance Support System for High-Security Engineering Environments

## What's working right now

- **Backend** runs with FastAPI + SQLite
- **Database** has two tables:
  - `faults` (title, owner, status)
  - `tools` (name, status)
- **API endpoints** live and tested at `/docs`:
  - `GET /api/faults` → list all faults
  - `POST /api/faults` → report a new fault
  - `GET /api/faults/{id}` → single fault
  - `PATCH /api/faults/{id}` → update fault status (open/closed)
  - `GET /api/tools` → list all tools
  - `POST /api/tools` → add a new tool
  - `GET /api/tools/{id}` → single tool (or 404)
  - `PATCH /api/tools/{id}` → update tool status (checked_in/checked_out)
  - `GET /health` → server health check
  - **Standard error format** active – all errors return `{ok: false, error: {type, message}}`
- **Pydantic schemas** include `FaultCreate`, `FaultOut`, `FaultUpdate` and the newly added `ToolCreate`, `ToolOut`, `ToolUpdate`
- **Dashboard** frontend at `/` shows a form to report faults and a live list
- **Static files** served from the `static/` folder (JS modules split as `api.js`, `ui.js`, `main.js`)

## Project structure

```
ar-project/
├── main.py              # FastAPI app and all routes (faults done, tools to be added)
├── database.py          # SQLite connection setup
├── models.py            # SQLAlchemy models for Fault and Tool
├── schemas.py           # Pydantic schemas for Fault and Tool input/output
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

