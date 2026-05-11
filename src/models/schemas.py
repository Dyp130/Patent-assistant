from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Project Schemas ---
class ProjectCreate(BaseModel):
    technical_concept: str = Field(..., min_length=10, description="核心技术构思描述")
    patent_type: str = Field(default="发明专利", description="专利类型：发明专利/实用新型/外观设计")


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    technical_concept: Optional[str] = None
    patent_type: Optional[str] = None
    status: Optional[str] = None


class ProjectSummary(BaseModel):
    id: int
    title: str
    patent_type: str
    status: str
    chapter_count: int = 0
    completed_chapters: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetail(BaseModel):
    id: int
    title: str
    technical_concept: str
    domain: str
    patent_type: str
    status: str
    chapters: list["ChapterSummary"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Chapter Schemas ---
class ChapterSummary(BaseModel):
    id: int
    chapter_order: int
    chapter_name: str
    chapter_key: str
    content: str
    status: str
    figure_placeholders: list = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterDetail(BaseModel):
    id: int
    project_id: int
    chapter_order: int
    chapter_name: str
    chapter_key: str
    content: str
    status: str
    figure_placeholders: list = []
    versions: list["VersionSummary"] = []
    figures: list["FigureSummary"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterUpdate(BaseModel):
    content: str = Field(..., description="编辑后的章节内容（Markdown格式）")


class GenerateChapterRequest(BaseModel):
    stream: bool = Field(default=False, description="是否使用SSE流式生成")


class GenerateAllRequest(BaseModel):
    stream: bool = Field(default=True, description="是否使用SSE流式生成")


# --- Version Schemas ---
class VersionSummary(BaseModel):
    id: int
    version_number: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Figure Schemas ---
class FigureSummary(BaseModel):
    id: int
    chapter_id: int
    position_label: str
    description: str
    content_type: str

    model_config = {"from_attributes": True}


class FigureUpdate(BaseModel):
    description: Optional[str] = None
    content_type: Optional[str] = None


# --- Export Schemas ---
class ExportRequest(BaseModel):
    format: str = Field(default="docx", description="导出格式：docx 或 markdown")


# --- Analysis Schemas ---
class ConceptAnalysis(BaseModel):
    core_inventive_concept: str = ""
    technical_problem: str = ""
    key_components: list[str] = []
    connection_types: list[str] = []
    novel_features: list[str] = []
    prior_art_gaps: list[str] = []
    technical_effects: list[str] = []
    suggested_terminology: dict = {}
