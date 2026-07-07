from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    school_id: int
    phone: str | None = None
    role: UserRole = UserRole.parent


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    school_id: int

    # lets this schema read straight from a SQLAlchemy object
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"