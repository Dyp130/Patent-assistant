from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    chapter_order: Mapped[int] = mapped_column(Integer)
    chapter_name: Mapped[str] = mapped_column(String(50))
    chapter_key: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="pending")
    figure_placeholders: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="chapters")
    versions = relationship("ChapterVersion", back_populates="chapter", order_by="ChapterVersion.version_number.desc()", cascade="all, delete-orphan")
    figures = relationship("FigurePlaceholder", back_populates="chapter", cascade="all, delete-orphan")


class ChapterVersion(Base):
    __tablename__ = "chapter_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    chapter = relationship("Chapter", back_populates="versions")
