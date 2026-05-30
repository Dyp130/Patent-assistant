import json
import asyncio
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.db import get_db
from src.models.project import Project
from src.models.chapter import Chapter
from src.models.figure import FigurePlaceholder
from src.models.schemas import GenerateAllRequest
from src.services.generation_service import (
    CHAPTER_KEY_MAP, CHAPTER_CONTENT_KEY,
    generate_chapter_sync, generate_chapter_stream,
    extract_figure_placeholders,
)
from src.services.analysis_service import analyze_concept
from src.services.prompt_loader import get_chapter_config

router = APIRouter(prefix="/api/projects/{project_id}/generate", tags=["generation"])


@router.post("/analyze")
def analyze_project_concept(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    analysis = analyze_concept(project.technical_concept)
    return analysis.model_dump()


@router.post("/chapter/{chapter_id}")
def generate_single_chapter(project_id: int, chapter_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    chapter = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.project_id == project_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    # Collect previous chapters for context
    analysis = analyze_concept(project.technical_concept)
    previous = _collect_previous(db, project_id, chapter.chapter_order)

    content = generate_chapter_sync(chapter.chapter_order, project.technical_concept, analysis, previous)
    _save_chapter_result(db, chapter, content)
    return {"content": content, "status": chapter.status, "figures": chapter.figure_placeholders}


@router.post("/chapter/{chapter_id}/stream")
async def generate_single_chapter_stream(project_id: int, chapter_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    chapter = db.query(Chapter).filter(Chapter.id == chapter_id, Chapter.project_id == project_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    analysis = analyze_concept(project.technical_concept)
    previous = _collect_previous(db, project_id, chapter.chapter_order)

    async def event_stream() -> AsyncGenerator[str, None]:
        full_content = ""
        try:
            async for token in generate_chapter_stream(
                chapter.chapter_order, project.technical_concept, analysis, previous
            ):
                full_content += token
                yield f"data: {json.dumps({'token': token})}\n\n"
                await asyncio.sleep(0)

            # Save result
            _save_chapter_result(db, chapter, full_content)
            figures = extract_figure_placeholders(full_content)
            yield f"data: {json.dumps({'done': True, 'figures': figures})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/all")
async def generate_all_stream(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    chapters = (
        db.query(Chapter)
        .filter(Chapter.project_id == project_id)
        .order_by(Chapter.chapter_order)
        .all()
    )

    analysis = analyze_concept(project.technical_concept)

    async def event_stream() -> AsyncGenerator[str, None]:
        previous: dict = {}
        for chapter in chapters:
            yield f"data: {json.dumps({'chapter_id': chapter.id, 'chapter_name': chapter.chapter_name, 'status': 'generating'})}\n\n"

            full_content = ""
            try:
                async for token in generate_chapter_stream(
                    chapter.chapter_order, project.technical_concept, analysis, previous
                ):
                    full_content += token
                    yield f"data: {json.dumps({'chapter_id': chapter.id, 'token': token})}\n\n"
                    await asyncio.sleep(0)
            except Exception as e:
                yield f"data: {json.dumps({'chapter_id': chapter.id, 'error': str(e)})}\n\n"
                continue

            _save_chapter_result(db, chapter, full_content)
            key = CHAPTER_CONTENT_KEY.get(chapter.chapter_order, chapter.chapter_key)
            previous[key] = full_content
            figures = extract_figure_placeholders(full_content)
            yield f"data: {json.dumps({'chapter_id': chapter.id, 'done': True, 'figures': figures})}\n\n"

        project.status = "reviewing"
        db.commit()
        yield f"data: {json.dumps({'all_done': True})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _collect_previous(db: Session, project_id: int, current_order: int) -> dict:
    """Collect previously generated chapter content for context chaining."""
    chapters = (
        db.query(Chapter)
        .filter(Chapter.project_id == project_id, Chapter.chapter_order < current_order)
        .order_by(Chapter.chapter_order)
        .all()
    )
    previous = {}
    for ch in chapters:
        key = CHAPTER_CONTENT_KEY.get(ch.chapter_order, ch.chapter_key)
        previous[key] = ch.content or ""
    return previous


def _save_chapter_result(db: Session, chapter: Chapter, content: str):
    """Save generated content, figures, and update chapter status."""
    chapter.content = content
    chapter.status = "ai_generated"

    # Clear old figure placeholders
    db.query(FigurePlaceholder).filter(FigurePlaceholder.chapter_id == chapter.id).delete()

    figures = extract_figure_placeholders(content)
    chapter.figure_placeholders = figures
    for f in figures:
        fp = FigurePlaceholder(
            chapter_id=chapter.id,
            position_label=f["position_label"],
            description=f["description"],
            position_marker=f["position_marker"],
            content_type="示意图",
        )
        db.add(fp)

    db.commit()
    db.refresh(chapter)
