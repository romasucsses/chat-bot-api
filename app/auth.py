from  .db.models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic import BaseModel
load_dotenv()


class LoginSchema(BaseModel):
    username: str
    password: str


class UserData(BaseModel):
    id: int
    is_active: bool
    plan_id: int | None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


AUTH_TOKENS_URL = os.environ['AUTH_TOKENS_SERVICE_URL']

async def get_tokens(user_data: UserData) -> dict:
    async with ClientSession() as session:
        async with session.post(AUTH_TOKENS_URL, json=user_data.dict()) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise HTTPException(status_code=response.status, detail="Failed to retrieve tokens")


async def login(login_data: LoginSchema, db: AsyncSession) -> dict:
    try:
        result = await db.execute(
            select(UserModel.id, UserModel.is_active, UserModel.hashed_password)
            .filter(UserModel.username == login_data.username)
        )
        user = result.first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        if not Hasher.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        user_data = UserData(id=user.id, is_active=user.is_active)
        tokens = await get_tokens(user_data=user_data)
        return tokens
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e



async def register(data: LoginSchema, db: AsyncSession) -> dict:
    try:
        get_user = await db.execute(select(UserModel).filter(UserModel.username == data.username))
        is_user_exist = get_user.scalar_one_or_none()
        if is_user_exist:
            raise HTTPException(status_code=400, detail='username is registered ')

        hashed_pass = Hasher.get_password_hash(data.password)
        new_user = UserModel(username=data.username, hashed_password=hashed_pass)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {'message': 'successfully registered'}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
