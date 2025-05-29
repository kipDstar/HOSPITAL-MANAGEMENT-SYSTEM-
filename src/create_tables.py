# src/create_tables.py

from src.database import engine
from src.models import Base

print("Creating all tables in the database...")
Base.metadata.create_all(bind=engine)
print("All tables created successfully.")
