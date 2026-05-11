from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Fault, User, Tool
from sqlalchemy import Column, String
from schemas import FaultCreate, FaultOut, FaultUpdate, UserCreate, ToolCreate, ToolOut, ToolUpdate
import bcrypt, jwt
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime, timedelta
from typing import Optional
import os
# Create tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AR Maintenance System")

from database import init_db
init_db()

#----------PRESET TEST ADMIN----------
def create_preset_admin():
    db = SessionLocal()
    existing = db.query(User).filter(User.username == "admin").first()
    
    if not existing:
        hashed = bcrypt.hashpw("admin123".encode(),bcrypt.gensalt())
        admin_user = User(username="admin", password=hashed.decode(), role="admin")
        db.add(admin_user)
        db.commit()
        
    db.close()


def create_preset_tools():
    db = SessionLocal()
    required_tools = [
        {"id": 1, "name": "Spanner"},
        {"id": 2, "name": "Screwdriver"},
        {"id": 3, "name": "Voltage tester"}
    ]

    for item in required_tools:
        tool = db.query(Tool).filter(Tool.id == item["id"]).first()
        if not tool:
            db.add(Tool(id=item["id"], name=item["name"], status="checked_in"))
        else:
            tool.name = item["name"]
            tool.status = "checked_in"

    db.commit()
    db.close()


def create_preset_faults():
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        db.close()
        return

    required_faults = [
        {"id": 1, "title": "Spanner issue", "location": "Marker 1", "severity": 1},
        {"id": 2, "title": "Screwdriver issue", "location": "Marker 2", "severity": 2},
        {"id": 3, "title": "Voltage tester issue", "location": "Marker 3", "severity": 3}
    ]

    for item in required_faults:
        fault = db.query(Fault).filter(Fault.id == item["id"]).first()
        if not fault:
            db.add(Fault(
                id=item["id"],
                title=item["title"],
                location=item["location"],
                severity=item["severity"],
                status="open",
                user_id=admin.id
            ))
        else:
            fault.title = item["title"]
            fault.location = item["location"]
            fault.severity = item["severity"]
            fault.status = "open"
            fault.user_id = admin.id

    db.commit()
    db.close()
        
create_preset_admin()
create_preset_tools()
create_preset_faults()

# -----Centralised error handlers------


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Standardises HTTP errors (404, 400, etc.) into the common shape."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": {
                "type": "http_error",
                "message": str(exc.detail)
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Returns 422 validation errors in the same consistent format."""
    return JSONResponse(
        status_code=422,
        content={
            "ok": False,
            "error": {
                "type": "validation_error",
                "message": "One or more fields are invalid.",
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catches unexpected server errors and hides tracebacks from the client."""
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": {
                "type": "server_error",
                "message": "An unexpected server error occurred."
            }
        }
    )

# Database session dependency 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
#JWT verification

security = HTTPBearer()

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_token(token=Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logging.warning("Token is Expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        logging.warning("Token is Invalid")
        raise HTTPException(status_code=403, detail="Invalid token")

def admin_required(user=Depends(verify_token)):
    role = str(user.get("role", "")).lower()
    if role not in ("admin", "supervisor"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
    
# ---------- FAULT ROUTES ----------

@app.get("/api/faults", response_model=list[FaultOut])
def list_faults(status: Optional[str] = None, db: Session = Depends(get_db), user=Depends(verify_token)):
    query = db.query(Fault)
    if status in ("open", "closed"):
        query = query.filter(Fault.status == status)
    return query.all()

@app.get("/api/faults/{fault_id}", response_model=FaultOut)
def get_fault(fault_id: int, db: Session = Depends(get_db), user=Depends(verify_token)):
    fault = db.query(Fault).filter(Fault.id == fault_id).first()
    if fault is None:
        raise HTTPException(status_code=404, detail="Fault not found")
    return fault

@app.post("/api/faults", response_model=FaultOut, status_code=201)
def create_fault(payload: FaultCreate, db: Session = Depends(get_db), user=Depends(verify_token)):
    db_user = db.query(User).filter(User.username == user["sub"]).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_fault = Fault(
        title=payload.title,
        location=payload.location,
        severity=payload.severity,
        user_id=db_user.id,
        status="open"
         )
    
    db.add(new_fault)
    db.commit()
    db.refresh(new_fault)
    return new_fault

@app.patch("/api/faults/{fault_id}", response_model=FaultOut)
def update_fault(fault_id: int, payload: FaultUpdate, db: Session = Depends(get_db), user=Depends(verify_token)):
    fault = db.query(Fault).filter(Fault.id == fault_id).first()
    if fault is None:
        raise HTTPException(status_code=404, detail="Fault not found")
    fault.status = payload.status
    db.commit()
    db.refresh(fault)
    return fault

# ---------- DELETE FAULT ----------

@app.delete("/api/faults/{fault_id}", status_code=204)
def delete_fault(fault_id: int, db: Session = Depends(get_db), user=Depends(admin_required)):
    fault = db.query(Fault).filter(Fault.id == fault_id).first()
    if fault is None:
        raise HTTPException(status_code=404, detail="Fault not found")
    db.delete(fault)
    db.commit()
    return

# ---------- TOOL ROUTES ----------

# Tool API endpoints
@app.get("/api/tools", response_model=list[ToolOut])
def list_tools(db: Session = Depends(get_db), user=Depends(verify_token)):
    """Return all tools from the database."""
    return db.query(Tool).all()


@app.post("/api/tools", response_model=ToolOut, status_code=201)
def create_tool(payload: ToolCreate, db: Session = Depends(get_db), user=Depends(verify_token)):
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
def get_tool(tool_id: int, db: Session = Depends(get_db), user=Depends(verify_token)):
    """Return a single tool by ID, or 404 if not found."""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()

    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")

    return tool


@app.patch("/api/tools/{tool_id}", response_model=ToolOut)
def update_tool(tool_id: int, payload: ToolUpdate, db: Session = Depends(get_db), user=Depends(verify_token)):
    """Update a tool's status (checked_in / checked_out)."""
    tool = db.query(Tool).filter(Tool.id == tool_id).first()

    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")

    tool.status = payload.status
    db.commit()
    db.refresh(tool)

    return tool

# ---------- RECENT ACTIVITY ----------

@app.get("/api/recent-activity")
def recent_activity(db: Session = Depends(get_db), user=Depends(verify_token)):
    """Return the 10 most recent fault updates for the activity feed."""
    recent = (
        db.query(Fault)
        .order_by(Fault.updated_at.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "id": f.id,
            "title": f.title,
            "location": f.location,
            "severity": f.severity,
            "status": f.status,
            "updated_at": f.updated_at.isoformat()
        }
        for f in recent
    ]

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

#----------- MIDDLEWARE -----------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) #controls cross-origin risks

#Password Hashing

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_change_me_to_a_long_random_string_32bytes_min") #env variables for exposure prevention
login_attempts = {}
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    
    role = "engineer"
    db_user = User(username=user.username, password=hashed.decode(), role=role)
    db.add(db_user)
    db.commit()
    
    return {"message": "User created"}

@app.post("/login")
def login(user:UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if user.username not in login_attempts:
        login_attempts[user.username] = 0
    
    if not db_user:
        login_attempts[user.username] += 1
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not bcrypt.checkpw(user.password.encode(), db_user.password.encode()):
        login_attempts[user.username] += 1
        if login_attempts[user.username] > 5:
            raise HTTPException (status_code=429, detail="Too many failed attempts")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    login_attempts[user.username] = 0
    
    token = create_token({"sub": db_user.username, "role": db_user.role})
    
    return {"access_token": token, "token_type": "bearer"}

   
#Route Protection

@app.get("/api/secure/faults", response_model=list[FaultOut])
def list_faults_protected(status: Optional[str] = None,
                db: Session = Depends(get_db),
                user=Depends(verify_token)
):
    query = db.query(Fault)
    if status in ("open", "closed"):
        query = query.filter(Fault.status == status)
    return query.all()


#logging

logging.basicConfig(level=logging.INFO)

@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response



# Home page
@app.get("/")
def home():
    return FileResponse("static/index.html")

# AR page
@app.get("/ar")
def ar_page():
    return FileResponse("static/ar.html")

# Supervisor Dashboard page
@app.get("/dashboard")
def dashboard_page():
    return FileResponse("static/dashboard.html")