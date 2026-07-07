from sqlalchemy import text
from app.db.session import engine

with engine.connect() as conn:
    version = conn.execute(text("SELECT version()")).scalar()
    print("Connected to Neon!")
    print(version)