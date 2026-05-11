from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base


class FigurePlaceholder(Base):
    __tablename__ = "figure_placeholders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"))
    position_label: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text, default="")
    position_marker: Mapped[int] = mapped_column(Integer, default=0)
    content_type: Mapped[str] = mapped_column(String(30), default="结构示意图")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    chapter = relationship("Chapter", back_populates="figures")
