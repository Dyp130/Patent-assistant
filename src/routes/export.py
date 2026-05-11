from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.db import get_db
from src.models.project import Project
from src.models.schemas import ExportRequest
from src.services.export_service import export_to_docx, export_to_markdown

router = APIRouter(prefix="/api/projects/{project_id}/export", tags=["export"])


@router.post("/docx")
def export_docx(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    filepath = export_to_docx(project)
    return {"filepath": filepath, "filename": filepath.name}


@router.get("/download/{filename}")
def download_export(project_id: int, filename: str):
    from config.settings import get_settings
    settings = get_settings()
    filepath = Path(settings.output_dir) / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(str(filepath), filename=filename, media_type="application/octet-stream")


from pathlib import Path


@router.post("/markdown")
def export_markdown(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    filepath = export_to_markdown(project)
    return {"filepath": filepath, "filename": filepath.name}
