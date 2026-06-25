from pydantic import BaseModel
from uuid import UUID

class ComparisonCreate(BaseModel):
    document_1_id: UUID
    document_2_id: UUID

class ComparisonUpdate(BaseModel):
    text_score: float | None = None
    code_score: float | None = None
    phrase_score: float | None = None
    final_score: float | None = None
    is_plagiat: bool | None = None

# class JobResponse(BaseModel):
#     id: int
#     name: str
#     email: str

#     class Config:
#         from_attributes = True
