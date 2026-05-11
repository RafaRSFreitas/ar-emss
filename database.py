from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./maintenance.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}, echo=True, future=True
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

Base = declarative_base()

#--------- DB INIT ----------

def init_db():
    import models 
    Base.metadata.create_all(bind=engine)