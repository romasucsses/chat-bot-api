from .config import *
import jwt
from .auth import UserData
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
from  .db.models import RefreshTokenModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from fastapi import HTTPException, status
from .schemas import UserData, RefreshTokenRequest
from sqlalchemy.exc import SQLAlchemyError


async def generate_token(token_type: str, user_data: UserData) -> str:
    if token_type not in {'access', 'refresh'}:
        raise ValueError("Invalid token type. Choose either 'access' or 'refresh'.")

    expiration = EXPIRATION_REFRESH_TOKEN if token_type == 'access' else EXPIRATION_REFRESH_TOKEN
    payload = {
        'user_id': user_data.id,
        'exp': datetime.datetime.utcnow() + expiration,
    }

    if token_type == 'access':
        payload.update({
            'is_active': user_data.is_active,
            'plan': user_data.plan_id
        })

    token = jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM_JWT)
    return token


async def create_tokens(db: AsyncSession, user_data: UserData) -> dict:
    try:
        access_token = await generate_token(token_type='access', user_data=user_data)
        refresh_token = await generate_token(token_type='refresh', user_data=user_data)

        now = datetime.datetime.utcnow()
        expires_in = int(now.timestamp()) + int(EXPIRATION_REFRESH_TOKEN.total_seconds())

        new_refresh_token = RefreshTokenModel(
            refresh_token=refresh_token,
            user_id=user_data.id,
            is_active=user_data.is_active,
            plan_id=user_data.plan_id,
            expires_in=expires_in
        )
        db.add(new_refresh_token)
        await db.commit()

        return {"access_token": access_token, "refresh_token": refresh_token}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred.")



async def login_handler(db: AsyncSession, user_data: UserData):
    try:
        existing_token = await db.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_data.id)
        )
        token_row = existing_token.scalar_one_or_none()
        now = datetime.datetime.utcnow()
        if token_row:
            if token_row.expires_in < now.timestamp():
                await db.execute(delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user_data.id))
                await db.commit()
                return await create_tokens(db, user_data)

            access_token = await generate_token(token_type='access', user_data=user_data)
            return {"access_token": access_token, "refresh_token": token_row.refresh_token}

        else:
            return await create_tokens(db, user_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def refresh_access_token(token: RefreshTokenRequest, db: AsyncSession) -> dict:
    try:
        result = await db.execute(
            select(RefreshTokenModel.user_id, RefreshTokenModel.user_permission, RefreshTokenModel.user_store_id)
            .where(RefreshTokenModel.refresh_token == token.refresh_token)
        )

        token_data = result.first()
        if not token_data:
            raise HTTPException(status_code=404, detail="Token not found.")

        user_data = UserData(
            id=token_data.user_id,
            is_active=token_data.is_active,
            plan_id=token_data.plan_id,
        )
        access_token = await generate_token(token_type='access', user_data=user_data)
        return {"access_token": access_token}
    except PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid Token')



async def delete_token_logout(db: AsyncSession, token: RefreshTokenRequest = None, user_id: int = None) -> dict:
    try:
        if user_id:
            get_refresh_token = await db.execute(
                select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id)
            )
        else:
            get_refresh_token = await db.execute(
                select(RefreshTokenModel).where(RefreshTokenModel.refresh_token == token.refresh_token)
            )
        refresh_token_instance = get_refresh_token.scalar_one_or_none()
        if not refresh_token_instance:
            raise HTTPException(status_code=404, detail="Refresh token not found.")

        await db.delete(refresh_token_instance)
        await db.commit()
        return {"message": "Token deleted"}
    except PyJWTError:
        raise HTTPException(status_code=401, detail='Invalid Token')