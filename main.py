from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Fault, Tool
from schemas import FaultCreate, FaultOut, FaultUpdate, ToolCreate, ToolOut, ToolUpdate
from typing import Optional


# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AR Maintenance System")

# Database session dependency 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- FAULT ROUTES ----------

@app.get("/api/faults", response_model=list[FaultOut])
def list_faults(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Fault)
    if status in ("open", "closed"):
        query = query.filter(Fault.status == status)
    return query.all()

@app.get("/api/faults/{fault_id}", response_model=FaultOut)
def get_fault(fault_id: int, db: Session = Depends(get_db)):
    fault = db.query(Fault).filter(Fault.id == fault_id).first()
    if fault is None:
        raise HTTPException(status_code=404, detail="Fault not found")
    return fault

@app.post("/api/faults", response_model=FaultOut, status_code=201)
def create_fault(payload: FaultCreate, db: Session = Depends(get_db)):
    new_fault = Fault(
        title=payload.title,
        location=payload.location,
        severity=payload.severity,
        status="open"
    )
    db.add(new_fault)
    db.commit()
    db.refresh(new_fault)
    return new_fault

@app.patch("/api/faults/{fault_id}", response_model=FaultOut)
def update_fault(fault_id: int, payload: FaultUpdate, db: Session = Depends(get_db)):
    fault = db.query(Fault).filter(Fault.id == fault_id).first()
    if fault is None:
        raise HTTPException(status_code=404, detail="Fault not found")
    fault.status = payload.status
    db.commit()
    db.refresh(fault)
    return fault

# ---------- TOOL ROUTES ----------

# Tool API endpoints
@app.get("/api/tools", response_model=list[ToolOut])
def list_tools(db: Session = Depends(get_db)):
    """Return all tools from the database."""
    return db.query(Tool).all()


@app.post("/api/tools", response_model=ToolOut, status_code=201)
def create_tool(payload: ToolCreate, db: Session = Depends(get_db)):
    """Create a new tool. Always starts as checked_in."""
    new_tool = Tool(
        name=payload.name,
        status="checked_in"   # default, but explicit is clearer
    )

    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)

    return new_tool


@app.get("/api/tools/{tool_id}", response_model=ToolOut)
def get_tool(tool_id: int, db: Session = Depends(get_db)):
    """Return a single tool by ID, or 404 if not found."""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()

    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")

    return tool


@app.patch("/api/tools/{tool_id}", response_model=ToolOut)
def update_tool(tool_id: int, payload: ToolUpdate, db: Session = Depends(get_db)):
    """Update a tool's status (checked_in / checked_out)."""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()

    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")

    tool.status = payload.status
    db.commit()
    db.refresh(tool)

    return tool

# ---------- STATIC FILES & HOME PAGE ----------

# Serve static files 
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check 
@app.get("/health")
def health():
    return {"status": "ok"}

# Home page
@app.get("/")
def home():
    return FileResponse("static/index.html")