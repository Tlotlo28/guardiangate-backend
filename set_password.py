from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password

EMAIL = "soaka@example.com"      # match Soaka's email in your users table
NEW_PASSWORD = "soaka1234"

db = SessionLocal()
user = db.execute(select(User).where(User.email == EMAIL)).scalar_one_or_none()
if user:
    user.hashed_password = hash_password(NEW_PASSWORD)
    db.commit()
    print(f"Password set for {user.full_name} ({EMAIL})")
else:
    print("User not found - check the EMAIL value")
db.close()