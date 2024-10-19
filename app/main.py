from fastapi import FastAPI
from pydantic import BaseModel
from .chat_service import chat_bot
from fastapi import APIRouter, Depends, Request
from .db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .auth import login, register, LoginSchema

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    user_id: int

@app.post('/chat-with-bot')
async def chat_with_bot_api(
        chat_data: ChatRequest
):
    response = await chat_bot(user_message=chat_data.message, user_id=chat_data.user_id)
    return {'response': response}


@app.post('/login')
async def login_api(
        login_data: LoginSchema,
        db: AsyncSession = Depends(get_db)
):
    return await login(login_data, db)


@app.post('/register')
async def registration_api(
        login_data: LoginSchema,
        db: AsyncSession = Depends(get_db)
):
    return await register(login_data, db)
