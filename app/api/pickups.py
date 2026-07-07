from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.learner import Learner
from app.models.guardian import GuardianLink
from app.models.pickup import PickupEvent, PickupStatus
from app.schemas.pickup import LearnerScanOut, GuardianOut, PickupCreate, PickupOut

router = APIRouter(prefix="/pickups", tags=["pickups"])

STAFF_ROLES = ("guard", "staff", "admin")


def serialize_pickup(event: PickupEvent) -> PickupOut:
    return PickupOut(
        id=event.id,
        learner_id=event.learner_id,
        learner_name=event.learner.full_name,
        learner_grade=event.learner.grade,
        guardian_id=event.guardian_id,
        guardian_name=event.guardian.full_name if event.guardian else None,
        guard_id=event.guard_id,
        status=event.status,
        requested_at=event.requested_at,
        responded_at=event.responded_at,
        released_at=event.released_at,
        note=event.note,
    )


@router.get("/scan/{qr_token}", response_model=LearnerScanOut)
def scan_learner(
    qr_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*STAFF_ROLES)),
):
    learner = db.execute(
        select(Learner).where(Learner.qr_token == qr_token)
    ).scalar_one_or_none()
    if learner is None or learner.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Learner not found")

    links = db.execute(
        select(GuardianLink).where(GuardianLink.learner_id == learner.id)
    ).scalars().all()
    guardians = [
        GuardianOut(
            guardian_id=link.guardian_id,
            full_name=link.guardian.full_name,
            relationship_label=link.relationship_label,
            phone=link.guardian.phone,
            can_collect=link.can_collect,
        )
        for link in links
    ]
    return LearnerScanOut(
        id=learner.id,
        full_name=learner.full_name,
        grade=learner.grade,
        photo_url=learner.photo_url,
        approved_guardians=guardians,
    )


@router.post("", response_model=PickupOut, status_code=201)
def create_pickup(
    payload: PickupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*STAFF_ROLES)),
):
    learner = db.get(Learner, payload.learner_id)
    if learner is None or learner.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Learner not found")

    link = db.execute(
        select(GuardianLink).where(
            GuardianLink.learner_id == learner.id,
            GuardianLink.guardian_id == payload.guardian_id,
            GuardianLink.can_collect == True,
        )
    ).scalar_one_or_none()
    if link is None:
        raise HTTPException(
            status_code=400,
            detail="This person is not an approved collector for this learner",
        )

    event = PickupEvent(
        learner_id=learner.id,
        guardian_id=payload.guardian_id,
        guard_id=current_user.id,
        status=PickupStatus.pending,
        note=payload.note,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return serialize_pickup(event)


@router.post("/{pickup_id}/approve", response_model=PickupOut)
def approve_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(PickupEvent, pickup_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Pickup not found")
    if event.guardian_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the collector for this pickup")
    if event.status != PickupStatus.pending:
        raise HTTPException(status_code=409, detail=f"Pickup is already {event.status.value}")

    event.status = PickupStatus.approved
    event.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(event)
    return serialize_pickup(event)


@router.post("/{pickup_id}/deny", response_model=PickupOut)
def deny_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = db.get(PickupEvent, pickup_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Pickup not found")
    if event.guardian_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the collector for this pickup")
    if event.status != PickupStatus.pending:
        raise HTTPException(status_code=409, detail=f"Pickup is already {event.status.value}")

    event.status = PickupStatus.denied
    event.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(event)
    return serialize_pickup(event)


@router.post("/{pickup_id}/release", response_model=PickupOut)
def release_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*STAFF_ROLES)),
):
    """The guard hands the child over - ONLY if the pickup is approved."""
    event = db.get(PickupEvent, pickup_id)
    if event is None or event.learner.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Pickup not found")
    if event.status != PickupStatus.approved:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot release - pickup is {event.status.value}, must be approved first",
        )

    event.status = PickupStatus.released
    event.released_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(event)
    return serialize_pickup(event)


@router.get("", response_model=list[PickupOut])
def list_pickups(
    status: PickupStatus | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*STAFF_ROLES)),
):
    """The dashboard feed: this school's pickups, newest first, optionally filtered by status."""
    stmt = (
        select(PickupEvent)
        .join(Learner)
        .where(Learner.school_id == current_user.school_id)
    )
    if status is not None:
        stmt = stmt.where(PickupEvent.status == status)
    stmt = stmt.order_by(PickupEvent.requested_at.desc())

    events = db.execute(stmt).scalars().all()
    return [serialize_pickup(e) for e in events]

@router.get("/my", response_model=list[PickupOut])
def my_pickups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """A parent's read-only history of their own children's pickups."""
    # step 1: which learners is this user a guardian of?
    learner_ids = db.execute(
        select(GuardianLink.learner_id).where(
            GuardianLink.guardian_id == current_user.id
        )
    ).scalars().all()

    if not learner_ids:
        return []

    # step 2: all pickups for those learners, newest first
    events = db.execute(
        select(PickupEvent)
        .where(PickupEvent.learner_id.in_(learner_ids))
        .order_by(PickupEvent.requested_at.desc())
    ).scalars().all()

    return [serialize_pickup(e) for e in events]

@router.get("/{pickup_id}", response_model=PickupOut)
def get_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*STAFF_ROLES)),
):
    """Fetch a single pickup by id (staff, own school) - used to poll status."""
    event = db.get(PickupEvent, pickup_id)
    if event is None or event.learner.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Pickup not found")
    return serialize_pickup(event)