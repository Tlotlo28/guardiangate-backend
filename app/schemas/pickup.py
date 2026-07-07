from datetime import datetime

from pydantic import BaseModel

from app.models.pickup import PickupStatus


class GuardianOut(BaseModel):
    guardian_id: int
    full_name: str
    relationship_label: str
    phone: str | None
    can_collect: bool


class LearnerScanOut(BaseModel):
    id: int
    full_name: str
    grade: str | None
    photo_url: str | None
    approved_guardians: list[GuardianOut]


class PickupCreate(BaseModel):
    learner_id: int
    guardian_id: int          # which approved guardian is collecting
    note: str | None = None


class PickupOut(BaseModel):
    id: int
    learner_id: int
    learner_name: str
    learner_grade: str | None
    guardian_id: int | None
    guardian_name: str | None
    guard_id: int | None
    status: PickupStatus
    requested_at: datetime
    responded_at: datetime | None
    released_at: datetime | None
    note: str | None