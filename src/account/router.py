from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from src.database import get_async_session
from src.auth.auth import current_user
from src.account.schemas import AccountCreate, AccountRead
from src.models.models import User, Account, Operation
from src.utils import AccountReadDTO


router = APIRouter(
    prefix="/account",
    tags=["Account"]
)

@router.post("/create_account")
async def create_account(data_account: AccountCreate, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    data = data_account.dict()
    data["user_id"] = user.id
    stmt = insert(Account).values(data)

    await session.execute(stmt)
    await session.commit()

    await FastAPICache().clear()
    
    return {"status": "success"}




@router.get("/get_accounts")
@cache(expire=120)
async def get_accounts(user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    subq = select(Operation.id).filter(Operation.account_id == Account.id).limit(4).order_by(Operation.created_at.desc()).scalar_subquery().correlate(Account)
    query = select(Account).outerjoin(Operation, Operation.id.in_(subq)).where(Account.user_id == user.id).options(contains_eager(Account.operation))
    res = await session.execute(query)
    result_orm = res.unique().scalars().all()
    
    result = [AccountReadDTO.model_validate(row, from_attributes=True) for row in result_orm]

    return result


@router.post("/change_account")
async def change_account(data_account: AccountRead, account_id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Account).where(Account.id == account_id)
        result = await session.execute(query)
        if result.scalar().user_id == user.id:
            data = data_account.dict()
            data["id"] = account_id
            stmt = update(Account).where(Account.id == account_id).values(data)

            await session.execute(stmt)
            await session.commit()

            await FastAPICache().clear()
            return {"status": "success"}
        else:
            raise Exception
        
    except Exception as e:
        return {"status": "not your account"}

@router.post("/delete_account")
async def delete_account(account_id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Account).where(Account.id == account_id)
        result = await session.execute(query)

        if result.scalar().user_id == user.id:
            stmt = delete(Account).where(Account.id == account_id)
            
            await session.execute(stmt)
            await session.commit()
            
            await FastAPICache().clear()
            return {"status": "success"}
        else:
            raise Exception
        
    except Exception as e:
        return {"status": "not your account", "detail": f"e"}
