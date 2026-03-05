import sys
import os
from sqlalchemy import text

# Add the project root to sys.path
sys.path.append(os.getcwd())

from apps.engine.db.session import engine, Base
from apps.engine.db.models import User, Content, Ledger

def recreate_database():
    print("--- Recreating Database ---")
    
    # 1. Drop existing tables (if any)
    # Since we are using SQLite, we can just delete the file, but let's be polite and drop metadata.
    # Actually, drop_all is safer if file locks exist.
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    # 2. Create all tables
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Database schema reset complete.")

if __name__ == "__main__":
    recreate_database()
