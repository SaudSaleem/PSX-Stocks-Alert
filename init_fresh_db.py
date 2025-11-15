"""
Initialize a fresh database with all tables
Run this once for a new database setup
"""
from app.database import engine
from app.models import Base

def init_db():
    """Create all tables"""
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()

