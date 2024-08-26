from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from src.database import get_async_session
from src.auth.auth import current_user
from src.wallet.schemas import WalletCreate, WalletReadDTO, WalletRead
from src.models.models import User, Wallet, Operation

router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"]
)

@router.post("/create_wallet")
async def create_wallet(data_wallet: WalletCreate, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    print(data_wallet)
    data = data_wallet.dict()
    data["user_id"] = user.id
    print(data)
    stmt = insert(Wallet).values(data)

    await session.execute(stmt)
    await session.commit()

    await FastAPICache().clear()
    
    return {"status": "success"}




@router.get("/get_wallets")
@cache(expire=120)
async def get_wallets(user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    subq = select(Operation.id).filter(Operation.wallet_id == Wallet.id).limit(4).order_by(Operation.created_at.desc()).scalar_subquery().correlate(Wallet)
    query = select(Wallet).outerjoin(Operation, Operation.id.in_(subq)).where(Wallet.user_id == user.id).options(contains_eager(Wallet.operations))
    res = await session.execute(query)
    result_orm = res.unique().scalars().all()
    
    result = [WalletReadDTO.model_validate(row, from_attributes=True) for row in result_orm]

    return result


@router.post("/change_wallet")
async def change_wallet(data_wallet: WalletRead, wallet_id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Wallet).where(Wallet.id == wallet_id)
        result = await session.execute(query)
        if result.scalar().user_id == user.id:
            data = data_wallet.dict()
            data["id"] = wallet_id
            stmt = update(Wallet).where(Wallet.id == wallet_id).values(data)

            await session.execute(stmt)
            await session.commit()

            await FastAPICache().clear()
            return {"status": "success"}
        else:
            raise Exception
        
    except Exception as e:
        return {"status": "not your wallet"}

@router.post("/delete_wallet")
async def delete_wallet(wallet_id: int, user: User = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Wallet).where(Wallet.id == wallet_id)
        result = await session.execute(query)

        if result.scalar().user_id == user.id:
            stmt = delete(Wallet).where(Wallet.id == wallet_id)
            
            await session.execute(stmt)
            await session.commit()
            
            await FastAPICache().clear()
            return {"status": "success"}
        else:
            raise Exception
        
    except Exception as e:
        return {"status": "not your wallet", "detail": f"e"}
