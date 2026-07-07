from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.notice import Notice, NoticeCategory
from app.schemas.notice import NoticeCreate, NoticeOut

router = APIRouter(prefix="/notices", tags=["notices"])


def serialize_notice(notice: Notice) -> NoticeOut:
    return NoticeOut(
        id=notice.id,
        title=notice.title,
        body=notice.body,
        category=notice.category,
        author_name=notice.author.full_name,
        created_at=notice.created_at,
    )


@router.post("", response_model=NoticeOut, status_code=201)
def create_notice(
    payload: NoticeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "staff")),
):
    """School staff post a notice to their school's parents."""
    notice = Notice(
        school_id=current_user.school_id,
        author_id=current_user.id,
        title=payload.title,
        body=payload.body,
        category=payload.category,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return serialize_notice(notice)


@router.get("", response_model=list[NoticeOut])
def list_notices(
    category: NoticeCategory | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Any logged-in user reads notices for THEIR school - parents included."""
    stmt = select(Notice).where(Notice.school_id == current_user.school_id)
    if category is not None:
        stmt = stmt.where(Notice.category == category)
    stmt = stmt.order_by(Notice.created_at.desc())

    notices = db.execute(stmt).scalars().all()
    return [serialize_notice(n) for n in notices]