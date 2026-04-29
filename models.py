from sqlalchemy import Column, Integer, String
from database import Base

# Database model for maintenance fault reports
class Fault(Base):
    __tablename__ = "faults"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    location = Column(String, nullable=False)
    severity = Column(Integer, default=1)
    status = Column(String, nullable=False, default="open")