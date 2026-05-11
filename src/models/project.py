from datetime import datetime
from sqlalchemy import String, Text, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), default="")
    technical_concept: Mapped[str] = mapped_column(Text, default="")
    domain: Mapped[str] = mapped_column(String(50), default="结构设计")
    patent_type: Mapped[str] = mapped_column(String(20), default="发明专利")
    status: Mapped[str] = mapped_column(String(20), default="drafting")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    chapters = relationship("Chapter", back_populates="project", order_by="Chapter.chapter_order", cascade="all, delete-orphan")
