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

# Database session dependency (Lab 3, page 15)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Serve static files (Lab 3, page 14)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Health check (Lab 1, page 6)
@app.get("/health")
def health():
    return {"status": "ok"}

# Temporary home page
@app.get("/")
def home():
    return {"message": "Backend running"}