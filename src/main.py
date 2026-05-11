from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

from src.db import init_db
from src.routes import projects, chapters, generation, figures, export


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Path("data").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)
    init_db()
    yield
    # Shutdown


app = FastAPI(title="专利撰写助手", version="0.1.0", lifespan=lifespan)

# Static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Templates — use FileSystemLoader with cache_size=0 to avoid Jinja2/Python 3.14 compat issue
_template_env = Environment(
    loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
    auto_reload=True,
    cache_size=0,
)
templates = Jinja2Templates(env=_template_env)

# API Routes
app.include_router(projects.router)
app.include_router(chapters.router)
app.include_router(generation.router)
app.include_router(figures.router)
app.include_router(export.router)


# Frontend page routes
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/project/{project_id}", response_class=HTMLResponse)
def project_page(project_id: int, request: Request):
    return templates.TemplateResponse(request, "project.html", {"project_id": project_id})


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "专利撰写助手"}
