from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.school import School
from app.models.user import User, UserRole
from app.models.learner import Learner
from app.models.guardian import GuardianLink


def seed():
    db = SessionLocal()
    try:
        # idempotent: if it already exists, don't create duplicates
        existing = db.execute(
            select(School).where(School.name == "Trinityhouse Centurion")
        ).scalar_one_or_none()
        if existing:
            print("Trinityhouse Centurion already seeded - skipping.")
            return

        school = School(name="Trinityhouse Centurion", address="Centurion, Gauteng")
        db.add(school)
        db.flush()  # push to DB so school.id exists - without committing yet

        parent = User(
            school_id=school.id,
            full_name="Soaka Lekota",
            email="soaka@example.com",
            phone="+27821234567",
            hashed_password="TEMP_SET_IN_PHASE_2",  # real hashing comes with auth
            role=UserRole.parent,
        )
        db.add(parent)
        db.flush()

        learner = Learner(
            school_id=school.id,
            full_name="Omphile Lekota",
            grade="Grade 3B",
        )
        db.add(learner)
        db.flush()

        link = GuardianLink(
            learner_id=learner.id,
            guardian_id=parent.id,
            relationship_label="Father",
            can_collect=True,
        )
        db.add(link)

        db.commit()  # save it all, permanently, in one transaction

        print("Seeded successfully:")
        print(f"  School:   {school.name}")
        print(f"  Parent:   {parent.full_name} ({parent.email})")
        print(f"  Learner:  {learner.full_name} - {learner.grade}")
        print(f"  QR token: {learner.qr_token}")
        print(f"  Link:     {parent.full_name} is {link.relationship_label} (can_collect={link.can_collect})")
    finally:
        db.close()


if __name__ == "__main__":
    seed()