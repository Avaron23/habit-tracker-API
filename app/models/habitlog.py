from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, DateTime, func
from datetime import datetime


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    habit_id: Mapped[int] = mapped_column(Integer, ForeignKey('habits.id', ondelete="CASCADE"), index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)