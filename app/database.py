from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment variable
# For local development, make sure to set DATABASE_URL in your .env file
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it in your .env file. "
        "Example: DATABASE_URL=postgresql://stocksuser:stockspass@localhost:5432/stocks_alert"
    )

# Fix for Heroku/some platforms that use 'postgres://' instead of 'postgresql://'
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# PostgreSQL configuration
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # Configure connection pooling for PostgreSQL
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL query debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 