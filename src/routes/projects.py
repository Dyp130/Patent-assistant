from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db import get_db
from src.models.project import Project
from src.models.chapter import Chapter
from src.models.schemas import ProjectCreate, ProjectUpdate, ProjectSummary, ProjectDetail
from src.services.prompt_loader import get_chapter_config

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectDetail)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(technical_concept=data.technical_concept, patent_type=data.patent_type)
    db.add(project)
    db.flush()

    # Auto-create chapter shells based on schema
    chapter_configs = get_chapter_config()
    for cfg in chapter_configs:
        ch = Chapter(
            project_id=project.id,
            chapter_order=cfg["order"],
            chapter_name=cfg["name"],
            chapter_key=cfg["key"],
        )
        db.add(ch)

    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectSummary])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.updated_at.desc()).all()
    result = []
    for p in projects:
        chapters = db.query(Chapter).filter(Chapter.project_id == p.id).all()
        result.append(ProjectSummary(
            id=p.id,
            title=p.title or "未命名项目",
            patent_type=p.patent_type,
            status=p.status,
            chapter_count=len(chapters),
            completed_chapters=sum(1 for c in chapters if c.status == "finalized"),
            created_at=p.created_at,
            updated_at=p.updated_at,
        ))
    return result


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.put("/{project_id}", response_model=ProjectDetail)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    db.delete(project)
    db.commit()
    return {"ok": True}
