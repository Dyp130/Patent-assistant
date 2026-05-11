from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.db import get_db
from src.models.project import Project
from src.models.chapter import Chapter, ChapterVersion
from src.models.schemas import ChapterSummary, ChapterDetail, ChapterUpdate

router = APIRouter(prefix="/api/projects/{project_id}/chapters", tags=["chapters"])


def _chapter_to_detail(chapter: Chapter) -> dict:
    vdata = [
        {"id": v.id, "version_number": v.version_number, "content": v.content, "created_at": v.created_at}
        for v in (chapter.versions or [])
    ]
    fdata = [
        {"id": f.id, "chapter_id": f.chapter_id, "position_label": f.position_label,
         "description": f.description, "content_type": f.content_type}
        for f in (chapter.figures or [])
    ]
    return {
        "id": chapter.id,
        "project_id": chapter.project_id,
        "chapter_order": chapter.chapter_order,
        "chapter_name": chapter.chapter_name,
        "chapter_key": chapter.chapter_key,
        "content": chapter.content,
        "status": chapter.status,
        "figure_placeholders": chapter.figure_placeholders or [],
        "versions": vdata,
        "figures": fdata,
        "created_at": chapter.created_at,
        "updated_at": chapter.updated_at,
    }


@router.get("", response_model=list[ChapterSummary])
def list_chapters(project_id: int, db: Session = Depends(get_db)):
    chapters = (
        db.query(Chapter)
        .filter(Chapter.project_id == project_id)
        .order_by(Chapter.chapter_order)
        .all()
    )
    return chapters


@router.get("/{chapter_id}", response_model=ChapterDetail)
def get_chapter(project_id: int, chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.project_id == project_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")
    return _chapter_to_detail(chapter)


@router.put("/{chapter_id}", response_model=ChapterDetail)
def update_chapter(project_id: int, chapter_id: int, data: ChapterUpdate, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.project_id == project_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    # Save version snapshot before updating
    if chapter.content and chapter.content != data.content:
        max_ver = (
            db.query(func.max(ChapterVersion.version_number))
            .filter(ChapterVersion.chapter_id == chapter_id)
            .scalar()
        ) or 0
        ver = ChapterVersion(
            chapter_id=chapter_id,
            version_number=max_ver + 1,
            content=chapter.content,
        )
        db.add(ver)

    chapter.content = data.content
    chapter.status = "user_edited"
    db.commit()
    db.refresh(chapter)
    return _chapter_to_detail(chapter)


@router.post("/{chapter_id}/versions/{version_id}/restore")
def restore_version(project_id: int, chapter_id: int, version_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.project_id == project_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    ver = db.query(ChapterVersion).filter(ChapterVersion.id == version_id, ChapterVersion.chapter_id == chapter_id).first()
    if not ver:
        raise HTTPException(status_code=404, detail="版本不存在")

    # Save current as new version before restoring
    if chapter.content:
        max_ver = (
            db.query(func.max(ChapterVersion.version_number))
            .filter(ChapterVersion.chapter_id == chapter_id)
            .scalar()
        ) or 0
        snapshot = ChapterVersion(chapter_id=chapter_id, version_number=max_ver + 1, content=chapter.content)
        db.add(snapshot)

    chapter.content = ver.content
    chapter.status = "user_edited"
    db.commit()
    db.refresh(chapter)
    return _chapter_to_detail(chapter)
