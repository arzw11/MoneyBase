from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from src.models.models import TypeOperation, Category


class OperationCreate(BaseModel):
    account_id: int
    category: Optional[Category]
    type_operation: Optional[TypeOperation]
    amount: float 

class OperationRead(BaseModel):
    id: int
    account_id: int
    category: Optional[Category]
    type_operation: Optional[TypeOperation]
    amount: float
    created_at: datetime
