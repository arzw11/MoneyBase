from typing import List
from pydantic import BaseModel

from src.account.schemas import AccountRead
from src.operations.schemas import OperationRead



class AccountReadDTO(AccountRead):
    operation: List["OperationRead"]