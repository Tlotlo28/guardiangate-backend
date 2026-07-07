from app.db.session import Base, engine
import app.models  # noqa: F401  -> importing registers all 5 models on Base

print("Creating tables in the database...")
Base.metadata.create_all(bind=engine)
print("Done. Tables now exist in Neon.")