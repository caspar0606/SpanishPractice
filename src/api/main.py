import logging
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

_LOG = logging.getLogger(__name__)


def _parse_cors_origins(raw: str) -> list[str]:
    out: list[str] = []
    for part in raw.split(","):
        o = part.strip().strip('"').strip("'")
        if o:
            out.append(o)
    return out


def _parse_cors_regex(raw: str | None) -> str | None:
    if not raw:
        return None
    s = raw.strip().strip('"').strip("'")
    return s or None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Spanish Practice API",
        version="1.0.0",
        description="API for Spanish writing, reading, and drills practice.",
    )

    # Cross-origin requests (e.g. Vercel front-end → Railway API) require CORS.
    # Set on Railway (or .env): CORS_ORIGINS=https://your-app.vercel.app
    # Optional: CORS_ORIGIN_REGEX=https://[a-zA-Z0-9-]+\\.vercel\\.app (preview URLs)
    _cors = _parse_cors_origins(os.getenv("CORS_ORIGINS", ""))
    _cors_regex = _parse_cors_regex(os.getenv("CORS_ORIGIN_REGEX"))
    if _cors or _cors_regex:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=_cors,
            allow_origin_regex=_cors_regex,
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        _LOG.warning(
            "CORS enabled: origins=%s regex=%s",
            _cors,
            _cors_regex,
        )
    else:
        _LOG.warning(
            "CORS disabled: set CORS_ORIGINS and/or CORS_ORIGIN_REGEX (no CORS headers will be sent)",
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

    @app.get("/health/cors", tags=["health"])
    def cors_health() -> dict:
        """What the running process sees (use to verify Railway env)."""
        origins = _parse_cors_origins(os.getenv("CORS_ORIGINS", ""))
        rx = _parse_cors_regex(os.getenv("CORS_ORIGIN_REGEX"))
        return {
            "cors_enabled": bool(origins or rx),
            "origins": origins,
            "origin_regex_configured": bool(rx),
        }

    frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
    static_dir = frontend_dir / "static"
    if frontend_dir.is_dir():

        @app.get("/")
        def serve_index() -> FileResponse:
            return FileResponse(frontend_dir / "index.html")

        if static_dir.is_dir():
            app.mount(
                "/static",
                StaticFiles(directory=str(static_dir)),
                name="frontend-static",
            )

    return app


app = create_app()
