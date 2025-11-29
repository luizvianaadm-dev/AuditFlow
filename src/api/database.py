from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# For development, we use SQLite.
# In production, this would be replaced by PostgreSQL connection string.
# Using /tmp to ensure write permissions in the sandbox environment if needed.
SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/auditflow.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
