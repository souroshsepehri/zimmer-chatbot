from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from core.config import settings

# Ensure database directory exists for SQLite
if "sqlite" in settings.database_url:
    # Handle relative paths (e.g., sqlite:///./app.db)
    db_url = settings.database_url.replace("sqlite:///", "")
    if db_url.startswith("./"):
        db_url = db_url[2:]  # Remove ./
    db_path = Path(db_url)
    # Create parent directory if it doesn't exist and path is not just filename
    if db_path.parent and str(db_path.parent) != "." and not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False  # Set to True for SQL query logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
