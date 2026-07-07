from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.learner import Learner
    from app.models.user import User


class AbsenceReport(Base):
    __tablename__ = "absence_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    learner_id: Mapped[int] = mapped_column(ForeignKey("learners.id"), nullable=False)
    reported_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    absence_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    learner: Mapped["Learner"] = relationship()
    reporter: Mapped["User"] = relationship()