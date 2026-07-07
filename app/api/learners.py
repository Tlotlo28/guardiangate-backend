from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.learner import Learner
from app.models.guardian import GuardianLink
from app.schemas.learner import LearnerOut

router = APIRouter(prefix="/learners", tags=["learners"])


@router.get("/my", response_model=list[LearnerOut])
def my_learners(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """The children the logged-in user is a guardian of."""
    ids = db.execute(
        select(GuardianLink.learner_id).where(
            GuardianLink.guardian_id == current_user.id
        )
    ).scalars().all()
    if not ids:
        return []
    learners = db.execute(
        select(Learner).where(Learner.id.in_(ids)).order_by(Learner.full_name)
    ).scalars().all()
    return learners