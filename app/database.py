from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable
# For local development, make sure to set DATABASE_URL in your .env file
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it in your .env file. "
        "Example: DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.xxx.supabase.co:5432/postgres"
    )

# Fix for Heroku/some platforms that use 'postgres://' instead of 'postgresql://'
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# PostgreSQL configuration optimized for Supabase
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # Configure connection pooling for cloud database (Supabase)
    pool_size=5,  # Reduced for cloud connections
    max_overflow=10,  # Reduced overflow
    pool_recycle=1800,  # Recycle connections every 30 minutes (keep connections alive longer)
    pool_pre_ping=True,  # Test connections before using
    pool_timeout=30,  # Wait up to 30 seconds for a connection from pool
    connect_args={
        "connect_timeout": 10,  # 10 second connection timeout
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
    echo=False  # Set to True for SQL query debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 