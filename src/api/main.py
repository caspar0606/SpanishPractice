from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    return app


app = create_app()
