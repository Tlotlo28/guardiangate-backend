import io
import zipfile

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.security import hash_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.learner import Learner
from app.models.guardian import GuardianLink
from app.schemas.admin import (
    LearnerCreate, LearnerUpdate, AdminLearnerOut,
    AdminUserCreate, UserUpdate, AdminUserOut,
    GuardianLinkCreate, GuardianLinkOut,
)
from app.services.badges import make_badge
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_ROLES = ("admin", "staff")


# ---------- Learners ----------
@router.post("/learners", response_model=AdminLearnerOut, status_code=201)
def create_learner(payload: LearnerCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    learner = Learner(school_id=current_user.school_id,
                      full_name=payload.full_name, grade=payload.grade)
    db.add(learner); db.commit(); db.refresh(learner)
    return learner


@router.get("/learners", response_model=list[AdminLearnerOut])
def list_learners(db: Session = Depends(get_db),
                  current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    return db.execute(
        select(Learner)
        .where(Learner.school_id == current_user.school_id, Learner.is_active == True)
        .order_by(Learner.full_name)
    ).scalars().all()


@router.patch("/learners/{learner_id}", response_model=AdminLearnerOut)
def update_learner(learner_id: int, payload: LearnerUpdate, db: Session = Depends(get_db),
                   current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    learner = db.get(Learner, learner_id)
    if learner is None or learner.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Learner not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(learner, k, v)
    db.commit(); db.refresh(learner)
    return learner


@router.delete("/learners/{learner_id}")
def deactivate_learner(learner_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    learner = db.get(Learner, learner_id)
    if learner is None or learner.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Learner not found")
    learner.is_active = False
    db.commit()
    return {"status": "deactivated", "id": learner_id}


# ---------- Users ----------
@router.post("/users", response_model=AdminUserOut, status_code=201)
def create_user(payload: AdminUserCreate, db: Session = Depends(get_db),
                current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(school_id=current_user.school_id, full_name=payload.full_name,
                email=payload.email, phone=payload.phone, role=payload.role,
                hashed_password=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    return user


@router.get("/users", response_model=list[AdminUserOut])
def list_users(role: UserRole | None = None, db: Session = Depends(get_db),
               current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    stmt = select(User).where(User.school_id == current_user.school_id, User.is_active == True)
    if role is not None:
        stmt = stmt.where(User.role == role)
    return db.execute(stmt.order_by(User.full_name)).scalars().all()


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    user = db.get(User, user_id)
    if user is None or user.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] != user.email:
        clash = db.execute(select(User).where(User.email == data["email"])).scalar_one_or_none()
        if clash:
            raise HTTPException(status_code=400, detail="Email already registered")
    for k, v in data.items():
        setattr(user, k, v)
    db.commit(); db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def deactivate_user(user_id: int, db: Session = Depends(get_db),
                    current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    user = db.get(User, user_id)
    if user is None or user.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")
    user.is_active = False
    db.commit()
    return {"status": "deactivated", "id": user_id}


# ---------- Guardian links ----------
@router.post("/guardian-links", response_model=GuardianLinkOut, status_code=201)
def create_guardian_link(payload: GuardianLinkCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    learner = db.get(Learner, payload.learner_id)
    if learner is None or learner.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Learner not found")
    guardian = db.get(User, payload.guardian_id)
    if guardian is None or guardian.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Guardian not found")
    link = GuardianLink(learner_id=learner.id, guardian_id=guardian.id,
                        relationship_label=payload.relationship_label,
                        can_collect=payload.can_collect)
    db.add(link); db.commit(); db.refresh(link)
    return GuardianLinkOut(id=link.id, learner_id=link.learner_id, guardian_id=link.guardian_id,
                           guardian_name=guardian.full_name, relationship_label=link.relationship_label,
                           can_collect=link.can_collect)


@router.get("/learners/{learner_id}/guardians", response_model=list[GuardianLinkOut])
def learner_guardians(learner_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    learner = db.get(Learner, learner_id)
    if learner is None or learner.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Learner not found")
    links = db.execute(select(GuardianLink).where(GuardianLink.learner_id == learner_id)).scalars().all()
    return [GuardianLinkOut(id=l.id, learner_id=l.learner_id, guardian_id=l.guardian_id,
                            guardian_name=l.guardian.full_name, relationship_label=l.relationship_label,
                            can_collect=l.can_collect) for l in links]


# ---------- Badges ----------
@router.get("/learners/{learner_id}/badge")
def learner_badge(learner_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    learner = db.get(Learner, learner_id)
    if learner is None or learner.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="Learner not found")
    png = make_badge(learner.full_name, learner.grade, learner.qr_token)
    fname = learner.full_name.replace(" ", "_") + "_badge.png"
    return Response(content=png, media_type="image/png",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@router.get("/badges-zip")
def badges_zip(db: Session = Depends(get_db),
               current_user: User = Depends(require_roles(*ADMIN_ROLES))):
    learners = db.execute(
        select(Learner).where(Learner.school_id == current_user.school_id, Learner.is_active == True)
        .order_by(Learner.full_name)
    ).scalars().all()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for l in learners:
            z.writestr(l.full_name.replace(" ", "_") + "_badge.png",
                       make_badge(l.full_name, l.grade, l.qr_token))
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition": 'attachment; filename="guardiangate_badges.zip"'})


class PasswordReset(BaseModel):
    new_password: str


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    payload: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(*ADMIN_ROLES)),
):
    target = db.get(User, user_id)
    if target is None or target.school_id != current_user.school_id:
        raise HTTPException(status_code=404, detail="User not found")
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    target.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"status": "password_reset", "id": user_id, "full_name": target.full_name}  