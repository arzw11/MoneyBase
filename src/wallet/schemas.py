from typing import List

from pydantic import BaseModel

from src.operations.schemas import OperationRead

class WalletCreate(BaseModel):
    name: str
    budget: float

class WalletRead(WalletCreate):
    id: int

class WalletReadDTO(WalletRead):
    operations: List["OperationRead"]