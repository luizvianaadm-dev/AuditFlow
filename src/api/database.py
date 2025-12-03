from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Read from environment variable or fallback to SQLite
# Handle PostgreSQL on Railway or SQLite locally
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgresql://"):
    # Railway PostgreSQL connection
    DATABASE_URL = db_url.replace("postgresql://", "postgresql+psycopg2://")
else:
    # Default to SQLite - use /tmp for better persistence in containers
    DATABASE_URL = "sqlite:////tmp/auditflow.db"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
