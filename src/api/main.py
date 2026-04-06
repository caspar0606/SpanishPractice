from fastapi import FastAPI

from src.api.routers.drills import router as drills_router
from src.api.routers.reading import router as reading_router
from src.api.routers.writing import router as writing_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Spanish Practice API",
        version="1.0.0",
        description="API for Spanish writing, reading, and drills practice."
    )

    app.include_router(writing_router, prefix="/writing", tags=["writing"])
    app.include_router(reading_router, prefix="/reading", tags=["reading"])
    app.include_router(drills_router, prefix="/drills", tags=["drills"])

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()