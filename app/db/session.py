from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Every model we create will inherit from this.
    It's how SQLAlchemy keeps a register of all our tables."""
    pass


# The engine = the pipe to Neon. Created once, reused everywhere.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,    # Neon drops idle connections; this checks the line is alive first
    echo=settings.DEBUG,   # prints the SQL it runs - great for learning, off in production
)

# A factory that hands out new sessions.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI dependency: opens a session for one request,
    and always closes it afterwards - even if something errors."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()