from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from database import Base

# Database model for maintenance fault reports
class Fault(Base):
    __tablename__ = "faults"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    severity = Column(Integer, default=1)
    status = Column(String, nullable=False, default="open")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", back_populates="faults")

# Database model for maintenance tools
class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer , primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="checked_in")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#User model for authentication & access control
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False) 
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="engineer")
    faults = relationship("Fault", back_populates="owner")
    
    #input size for strings retstained, payload attack prevention
    
