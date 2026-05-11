from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db import get_db
from src.models.figure import FigurePlaceholder
from src.models.schemas import FigureSummary, FigureUpdate

router = APIRouter(prefix="/api/projects/{project_id}/figures", tags=["figures"])


@router.get("", response_model=list[FigureSummary])
def list_project_figures(project_id: int, db: Session = Depends(get_db)):
    figures = (
        db.query(FigurePlaceholder)
        .join(FigurePlaceholder.chapter)
        .filter(FigurePlaceholder.chapter.has(project_id=project_id))
        .order_by(FigurePlaceholder.position_label)
        .all()
    )
    return figures


@router.put("/{figure_id}", response_model=FigureSummary)
def update_figure(project_id: int, figure_id: int, data: FigureUpdate, db: Session = Depends(get_db)):
    figure = db.query(FigurePlaceholder).filter(FigurePlaceholder.id == figure_id).first()
    if not figure:
        raise HTTPException(status_code=404, detail="附图标记不存在")
    if data.description is not None:
        figure.description = data.description
    if data.content_type is not None:
        figure.content_type = data.content_type
    db.commit()
    db.refresh(figure)
    return figure
