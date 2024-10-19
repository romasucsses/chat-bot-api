from .database import Base
from sqlalchemy import (Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class UserModel(Base):
    __tablename__ = 'user_model'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String)
    name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_joining = Column(Date, default=func.current_date())
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    plan_id = Column(Integer, ForeignKey("bot_plan_model.id"))
    plan = relationship("BotPlanModel", back_populates="children")


class BotPlanModel(Base):
    __tablename__ = 'bot_plan_model'

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float)
    model_access = Column(Integer)
    description = Column(String)


class RefreshTokenModel(Base):
    __tablename__ = 'refresh_token'

    id = Column(Integer, primary_key=True)
    refresh_token = Column(String, index=True)
    user_id = Column(Integer, index=True)
    user_permission = Column(String, default='client')
    user_store_id = Column(Integer, nullable=True)
    expires_in = Column(Integer)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())