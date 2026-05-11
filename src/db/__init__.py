from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import get_settings

settings = get_settings()

engine = create_engine(
    f"sqlite:///{settings.db_path}",
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from src.models.project import Project  # noqa: F401
    from src.models.chapter import Chapter, ChapterVersion  # noqa: F401
    from src.models.figure import FigurePlaceholder  # noqa: F401
    Base.metadata.create_all(bind=engine)
