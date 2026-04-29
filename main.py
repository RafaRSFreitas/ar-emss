import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Fault
from schemas import FaultCreate, FaultOut, FaultUpdate


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

from typing import Optional

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