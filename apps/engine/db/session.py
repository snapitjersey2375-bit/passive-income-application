import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Fallback to local SQLite if no external DB provided
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./nexusflow.db")

# SQLAlchemy requires 'postgresql://' instead of 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

is_sqlite = DATABASE_URL.startswith("sqlite")

# SQLite needs check_same_thread=False; Postgres gets a proper connection pool
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine_kwargs = dict(connect_args=connect_args)
if not is_sqlite:
    engine_kwargs.update(
        pool_size=10,          # Keep 10 persistent connections
        max_overflow=20,       # Allow up to 20 extra under burst load
        pool_pre_ping=True,    # Discard stale connections automatically
        pool_recycle=3600,     # Recycle connections every hour
    )

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
