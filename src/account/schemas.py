from pydantic import BaseModel


class AccountCreate(BaseModel):
    name: str
    budget: float

class AccountRead(BaseModel):
    id: int
    name: str
    budget: float
