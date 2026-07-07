from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.learner import Learner
from app.models.guardian import GuardianLink
from app.models.absence import AbsenceReport
from app.schemas.absence import AbsenceCreate, AbsenceOut

router = APIRouter(prefix="/absences", tags=["absences"])

STAFF_VIEW_ROLES = ("admin", "staff")


def serialize_absence(a: AbsenceReport) -> AbsenceOut:
    return AbsenceOut(
        id=a.id,
        learner_id=a.learner_id,
        learner_name=a.learner.full_name,
        reported_by=a.reported_by,
        reporter_name=a.reporter.full_name,
        absence_date=a.absence_date,
        reason=a.reason,
        created_at=a.created_at,
    )


@router.post("", response_model=AbsenceOut, status_code=201)
def report_absence(
    payload: AbsenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """A parent reports that their child will be absent."""
    learner = db.get(Learner, payload.learner_id)
    if learner is None:
        raise HTTPException(status_code=404, detail="Learner not found")

    # the reporter must be a guardian of this learner
    link = db.execute(
        select(GuardianLink).where(
            GuardianLink.learner_id == learner.id,
            GuardianLink.guardian_id == current_user.id,
        )
    ).scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=403, detail="You are not listed as a guardian of this learner")

    absence = AbsenceReport(
        learner_id=learner.id,
        reported_by=current_user.id,
        absence_date=payload.absence_date,
        reason=payload.reason,
    )
    db.add(absence)
    db.commit()
    db.refresh(absence)
    return serialize_absence(absence)


@router.get("", response_model=list[AbsenceOut])
def list_absences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Staff see every absence for their school; a parent sees only the ones they reported."""
    if current_user.role.value in STAFF_VIEW_ROLES:
        stmt = (
            select(AbsenceReport)
            .join(Learner)
            .where(Learner.school_id == current_user.school_id)
        )
    else:
        stmt = select(AbsenceReport).where(AbsenceReport.reported_by == current_user.id)
    stmt = stmt.order_by(AbsenceReport.absence_date.desc())

    reports = db.execute(stmt).scalars().all()
    return [serialize_absence(a) for a in reports]