import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.learner import Learner
    from app.models.user import User


class PickupStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    released = "released"
    denied = "denied"
    cancelled = "cancelled"


class PickupEvent(Base):
    __tablename__ = "pickup_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    learner_id: Mapped[int] = mapped_column(ForeignKey("learners.id"), nullable=False)
    guardian_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    guard_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    status: Mapped[PickupStatus] = mapped_column(
        Enum(PickupStatus), default=PickupStatus.pending, nullable=False
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    note: Mapped[str | None] = mapped_column(Text)

    learner: Mapped["Learner"] = relationship(back_populates="pickups")
    guardian: Mapped["User"] = relationship(foreign_keys=[guardian_id])
    guard: Mapped["User"] = relationship(foreign_keys=[guard_id])