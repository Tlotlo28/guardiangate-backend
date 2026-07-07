from datetime import date, datetime

from pydantic import BaseModel


class AbsenceCreate(BaseModel):
    learner_id: int
    absence_date: date
    reason: str


class AbsenceOut(BaseModel):
    id: int
    learner_id: int
    learner_name: str
    reported_by: int
    reporter_name: str
    absence_date: date
    reason: str
    created_at: datetime