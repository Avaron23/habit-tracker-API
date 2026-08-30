from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, DateTime, func
from datetime import datetime


class Habitlog(Base):
    __tablename__ = "habitslogs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey('habits.id'))
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())