from pydantic import BaseModel

class DocumentCreate(BaseModel):
    name: str

class DocumentUpdate(BaseModel):
    name: str | None = None
    status: str | None = None

