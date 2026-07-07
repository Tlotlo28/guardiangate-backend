from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class LearnerCreate(BaseModel):
    full_name: str
    grade: str | None = None


class AdminLearnerOut(BaseModel):
    id: int
    full_name: str
    grade: str | None
    qr_token: str

    model_config = {"from_attributes": True}


class AdminUserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: str | None = None
    role: UserRole = UserRole.parent


class AdminUserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    phone: str | None

    model_config = {"from_attributes": True}


class GuardianLinkCreate(BaseModel):
    learner_id: int
    guardian_id: int
    relationship_label: str
    can_collect: bool = True


class GuardianLinkOut(BaseModel):
    id: int
    learner_id: int
    guardian_id: int
    guardian_name: str
    relationship_label: str
    can_collect: bool

class LearnerUpdate(BaseModel):
    full_name: str | None = None
    grade: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None