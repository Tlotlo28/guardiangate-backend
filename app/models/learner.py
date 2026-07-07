import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.school import School
    from app.models.guardian import GuardianLink
    from app.models.pickup import PickupEvent


class Learner(Base):
    __tablename__ = "learners"

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)

    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(40))
    # random, unguessable code the guard scans - never the row id
    qr_token: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, default=lambda: uuid.uuid4().hex
    )
    photo_url: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    school: Mapped["School"] = relationship(back_populates="learners")
    guardians: Mapped[list["GuardianLink"]] = relationship(back_populates="learner")
    pickups: Mapped[list["PickupEvent"]] = relationship(back_populates="learner")