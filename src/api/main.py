import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

from src.api.routers.drills import router as drills_router
from src.api.routers.exercise_selection import router as exercise_router
from src.api.routers.progress import router as progress_router
from src.api.routers.reading import router as reading_router
from src.api.routers.user import router as user_router
from src.api.routers.writing import router as writing_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Spanish Practice API",
        version="1.0.0",
        description="API for Spanish writing, reading, and drills practice.",
    )

    _cors = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    if _cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=_cors,
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(user_router, prefix="/user", tags=["user"])
    app.include_router(exercise_router, prefix="/exercise", tags=["exercise"])
    app.include_router(progress_router, prefix="/progress", tags=["progress"])
    app.include_router(writing_router, prefix="/writing", tags=["writing"])
    app.include_router(reading_router, prefix="/reading", tags=["reading"])
    app.include_router(drills_router, prefix="/drills", tags=["drills"])

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
    if frontend_dir.is_dir():

        @app.get("/")
        def serve_index() -> FileResponse:
            return FileResponse(frontend_dir / "index.html")

        app.mount(
            "/static",
            StaticFiles(directory=str(frontend_dir)),
            name="frontend-static",
        )

    return app


app = create_app()
