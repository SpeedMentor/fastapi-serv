from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Get database credentials from environment variables (set in k8s secrets)
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "fastapi")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres-service")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Request(Base):
    __tablename__ = "requests"

    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data = Column(JSON)
    metadata = Column(JSON)

class Metrics(Base):
    __tablename__ = "metrics"

    id = Column(String, primary_key=True)
    request_id = Column(String, nullable=False)
    process_time = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    error_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    additional_data = Column(JSON)

# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
