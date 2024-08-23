import datetime
import enum

from re import M
import re
from typing import Annotated, List
from unicodedata import category

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

from sqlalchemy import Boolean, Float, String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )]

class Category(enum.Enum):
    food = "food"
    health = "health"
    tabacco = "tabacco"
    entertainment = "entertainment"  
    transportation = "transportation" 
    housing = "housing"                
    education = "education"            
    savings = "savings"               
    gifts = "gifts"                    
    salary = "salary"                 
    freelance = "freelance"           
    investment = "investment" 

class TypeOperation(enum.Enum):
    profit = "profit"
    loss = "loss"


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id: Mapped[intpk]
    username: Mapped[String] = mapped_column(String(length=30), nullable=False)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    accounts: Mapped[List["Account"]] = relationship(
        back_populates="user"
    )
    operations: Mapped[List["Operation"]] =relationship(
        back_populates="user_operations"
    )

class Account(Base):
    __tablename__ = "account"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(length=64), nullable=False, default="MyAccount")
    budget: Mapped[float] = mapped_column(Float(precision=2), nullable=False, default=0)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["User"] = relationship(
        back_populates="accounts"
    )
    operation: Mapped[List["Operation"]] = relationship(
        back_populates="account_operations"
    )


class Operation(Base):
    __tablename__ = "operation"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[Category] = mapped_column(String, nullable=False)
    type_operation: Mapped[TypeOperation] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float(precision=2), default=0, nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user_operations: Mapped["User"] = relationship(
        back_populates="operations"
    )

    account_operations: Mapped["Account"] = relationship(
        back_populates="operation"
    )