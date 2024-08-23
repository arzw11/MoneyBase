from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache


from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import query, session


from src.database import get_async_session
from src.account.schemas import AccountRead
from src.auth.auth import current_user
from src.models.models import Operation, TypeOperation, User, Account, Category
from src.operations.schemas import OperationCreate, OperationRead



router = APIRouter(
    prefix="/operation",
    tags=["Operations"]
)


@router.post("/add_operation")
async def add_operation(data_operation: OperationCreate, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    data = data_operation.dict()
    query = select(Account).where(Account.user_id == user.id)
    result = await session.execute(query)
    list_accounts = [AccountRead.model_validate(row, from_attributes=True) for row in result.scalars().all()]
    try:
        if any(map(lambda x: True if x.id == data["account_id"] else False, list_accounts)):
            data["user_id"] = user.id
            data["category"] = data_operation.category.value
            data["type_operation"] = data_operation.type_operation.value
            stmt = insert(Operation).values(data)
            if data_operation.type_operation.value == "profit":
                stmt2 = update(Account).where(Account.id == data["account_id"]).values(budget=Account.budget + data["amount"])
                
            else:
                stmt2 = update(Account).where(Account.id == data["account_id"]).values(budget=Account.budget - data["amount"])
            
            await session.execute(stmt)
            await session.execute(stmt2)
            await session.commit()

            await FastAPICache().clear()
            return {"status": "success", "detail": OperationCreate.model_validate(data, from_attributes=True)}
        
        else:
            return {"status": "fall", "detail": "Not your account."}
    except Exception as e:
        print(e)
        return {"status": "fall"}


@router.post("/delete_operation")
async def add_operation(operation_id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(Operation).where(Operation.user_id == user.id)
    res = await session.execute(query)
    result = [OperationRead.model_validate(row, from_attributes=True) for row in res.scalars().all()]
    operation = list(map(lambda x: x, filter(lambda x: x.id == operation_id, result)))
    print(operation[0].account_id)
    try:
        if operation:
            stmt_del = delete(Operation).where(Operation.id == operation_id)
            await session.execute(stmt_del)
            if operation[0].type_operation.value == "profit":
                stmt = update(Account).where(Account.id == operation[0].account_id).values(budget=Account.budget - operation[0].amount)
                
            else:
                stmt = update(Account).where(Account.id == operation[0].account_id).values(budget=Account.budget + operation[0].amount)

            await session.execute(stmt)
            await session.commit()

            await FastAPICache().clear()
            return {"status": "succes", "detail": result}

        else: 
            raise Exception
    except Exception as e:
        return {"status": "fall", "detail": "Not your account."}

@router.get("/get_all_operations")
@cache(expire=120)
async def get_all_operations(limit: int=5, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(Operation).where(Operation.user_id == user.id).limit(limit=limit).order_by(Operation.created_at.desc())
    res = await session.execute(query)

    result = [OperationRead.model_validate(row, from_attributes=True) for row in res.scalars().all()] 
    return result

@router.get("/get_category_operations")
@cache(expire=120)
async def get_category_operations(category: Optional[Category], limit: int=5, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(Operation).where(Operation.user_id == user.id, Operation.category == category.value).limit(limit=limit).order_by(Operation.created_at.desc())
    res = await session.execute(query)

    result = [OperationRead.model_validate(row, from_attributes=True) for row in res.scalars().all()]
    return result

@router.get("/get_all_profit_operations")
@cache(expire=120)
async def get_all_profit_operations(limit: int=5, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(Operation).where(Operation.user_id == user.id, Operation.type_operation == "profit").limit(limit=limit).order_by(Operation.created_at.desc())
    res = await session.execute(query)

    result = [OperationRead.model_validate(row, from_attributes=True) for row in res.scalars().all()] 
    return result

@router.get("/get_all_loss_operations")
@cache(expire=120)
async def get_all_loss_operations(limit: int=5, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(Operation).where(Operation.user_id == user.id, Operation.type_operation == "loss").limit(limit=limit).order_by(Operation.created_at.desc())
    res = await session.execute(query)

    result = [OperationRead.model_validate(row, from_attributes=True) for row in res.scalars().all()] 
    return result

@router.get("/get_profit_and_loss")
@cache(expire=120)
async def get_profit_and_loss(account_id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    query = select(func.sum(Operation.amount)).where(Operation.user_id == user.id, Operation.account_id == account_id).filter(Operation.type_operation.in_(["profit", "loss"])).group_by(Operation.type_operation)
    result = await session.execute(query)
    loss, profit = result.scalars().all()

    return {"profit": profit, "loss": loss}
    