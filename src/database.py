from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DATABASE_URL 
from src.models import Base

DATABASE_URL = "sqlite:///hospital.db"

# Here we are creating a SQLAlchemy engine that will connect to the db and manages the connection pool and dialects, will ad a debug statemnt to print all statemnts to the console
engine = create_engine(DATABASE_URL, echo=True)

# next we create a session class that will be used to create sessions to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# A Session is a "holding zone" for all objects loaded or associated with the database.
# 'autocommit=False': Transactions are not committed automatically. You need to call session.commit().
# 'autoflush=False': Objects are not flushed to the database automatically before query operations.
# 'bind=engine': Binds the session to our database engine.

# Next we create a declarative base method to return a base class for ORM models to inherit from
Base = declarative_base()
def create_tables():
    """
    Create all tables in the database.
    This function uses the Base metadata to create all tables defined in the ORM models.
    """
    print(f"Attempting to create tables in the database at the following URL: {DATABASE_URL}...")
    Base.metadata.create_all(engine)
    print("Tables created successfully.")

# we create a helper function to get a new database session
def get_db():
    """
    Returns a new SQLAlchemy session instance.
    This function is called whenever a database operation is needed
    to get a fresh session.
    It's important to close the session when done (session.close()).
    """
    db = SessionLocal()
    try:
        yield db # Use 'yield' for a context manager pattern (but since we dont know much on that),
                      # For now, a direct return is fine for simple CLI usage
    finally:
        db.close()

# for robust (realer) applications we can add the following block
from contextlib import contextmanager
@contextmanager
def get_db_context():
    """
    Context manager for database sessions.
    This function provides a context manager that automatically handles session creation and closure.
    """
    session = Session()
    try:
        yield session
    except Exception: # If an exception occurs, rollback the session to avoid committing partial changes
        print("An error occurred, rolling back the session.")
        session.rollback() # Rollback the session in case of an error meaning the transaction will not be committed
        raise
    finally:
        session.close()