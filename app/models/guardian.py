from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.learner import Learner
    from app.models.user import User


class GuardianLink(Base):
    __tablename__ = "guardian_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    learner_id: Mapped[int] = mapped_column(ForeignKey("learners.id"), nullable=False)
    guardian_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    relationship_label: Mapped[str] = mapped_column(String(60), nullable=False)  # Mother, Father, Driver...
    can_collect: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    learner: Mapped["Learner"] = relationship(back_populates="guardians")
    guardian: Mapped["User"] = relationship()  # the parent/collector (a User)