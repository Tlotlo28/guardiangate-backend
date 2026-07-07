from pydantic import BaseModel


class LearnerOut(BaseModel):
    id: int
    full_name: str
    grade: str | None

    model_config = {"from_attributes": True}