# src/database.py

import sys # Needed for sys.stderr and sys.exit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DATABASE_URL 
from src.models import Base


# For now, DATABASE_URL is hardcoded for debugging.
DATABASE_URL = "sqlite:///hospital.db" # This will create hospital.db in your project root

try:
    # Added explicit flush=True to ensure immediate printing
    print("DEBUG: Attempting to create engine...", file=sys.stdout, flush=True)
    engine = create_engine(DATABASE_URL, echo=True)
    print("DEBUG: Engine created successfully.", file=sys.stdout, flush=True)
except Exception as e:
    # This print statement should be seen if any error occurs during engine creation
    print(f"FATAL ERROR: Failed to create SQLAlchemy engine: {e}", file=sys.stderr, flush=True)
    import traceback # Ensure this is imported for the traceback
    traceback.print_exc(file=sys.stderr) # Prints full traceback
    sys.exit(1) # Forces the script to exit with an error code


# Create a session class to interact with the database.
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create a declarative base class for ORM models to inherit from.
Base = declarative_base()

def create_tables():
    """
    Creates all database tables defined in the ORM models.
    """
    print(f"Attempting to create tables in the database at URL: {DATABASE_URL}...", file=sys.stdout, flush=True)
    Base.metadata.create_all(engine)
    print("Tables created successfully.", file=sys.stdout, flush=True)

# Helper function to get a new database session instance.
def get_db():
    """
    Provides a new SQLAlchemy session instance.
    """
    session = session()
    try:
        yield session
    finally:
        db.close()

# Context manager for more robust session handling.
from contextlib import contextmanager
@contextmanager
def get_db_context():
    """
    Provides a context manager for database sessions.
    """
    session = Session()
    try:
        yield session
    except Exception:
        print("An error occurred, rolling back the session.", file=sys.stderr, flush=True)
        session.rollback()
        raise
    finally:
        session.close()