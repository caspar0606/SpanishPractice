import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

from src.api.deps import current_username
from src.api.routers.chat import router as chat_router
from src.api.routers.drills import router as drills_router
from src.api.routers.exercise_selection import router as exercise_router
from src.api.routers.learn import router as learn_router
from src.api.routers.listening import router as listening_router
from src.api.routers.onboarding import router as onboarding_router
from src.api.routers.progress import router as progress_router
from src.api.routers.reading import router as reading_router
from src.api.routers.speaking import router as speaking_router
from src.api.routers.translate import router as translate_router
from src.api.routers.user import router as user_router
from src.api.routers.vocab import router as vocab_router
from src.api.routers.writing import router as writing_router
from src.application.container import Deps, configure
from src.application import container as app_container
from src.domain.models.user import User
from src.infrastructure.audio import cache as audio_cache
from src.infrastructure.wiring import (
    build_content_repository,
    build_dictionary_gateway,
    build_llm_gateway,
    build_stt_gateway,
    build_tts_gateway,
    build_user_repository,
)

_LOG = logging.getLogger(__name__)


def _clip_in_prompt(prompt: object, clip_id: str) -> bool:
    return isinstance(prompt, dict) and prompt.get("clip_id") == clip_id


def _user_owns_clip(user: User, clip_id: str) -> bool:
    current = user.current_exercise
    if current is not None and _clip_in_prompt(current.prompt, clip_id):
        return True
    return any(_clip_in_prompt(item.prompt, clip_id) for item in user.exercise_history)


def configure_container() -> None:
    """Bind application ports to infrastructure adapters.

    This is the only place that knows about both layers.
    """
    configure(
        Deps(
            users=build_user_repository(),
            llm=build_llm_gateway(),
            content=build_content_repository(),
            tts=build_tts_gateway(),
            stt=build_stt_gateway(),
            dictionary=build_dictionary_gateway(),
        ),
    )


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
    configure_container()

    docs_on = os.getenv("DOCS_ENABLED", "").strip().lower() in {"1", "true", "yes"}
    app = FastAPI(
        title="Spanish Practice API",
        version="2.0.0",
        description="API for Spanish writing, reading, listening, speaking, and drills practice.",
        docs_url="/docs" if docs_on else None,
        redoc_url="/redoc" if docs_on else None,
        openapi_url="/openapi.json" if docs_on else None,
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
    app.include_router(onboarding_router, prefix="/onboarding", tags=["onboarding"])
    app.include_router(exercise_router, prefix="/exercise", tags=["exercise"])
    app.include_router(progress_router, prefix="/progress", tags=["progress"])
    app.include_router(writing_router, prefix="/writing", tags=["writing"])
    app.include_router(reading_router, prefix="/reading", tags=["reading"])
    app.include_router(drills_router, prefix="/drills", tags=["drills"])
    app.include_router(listening_router, prefix="/listening", tags=["listening"])
    app.include_router(speaking_router, prefix="/speaking", tags=["speaking"])
    app.include_router(learn_router, prefix="/learn", tags=["learn"])
    app.include_router(chat_router, prefix="/chat", tags=["chat"])
    app.include_router(vocab_router, prefix="/vocab", tags=["vocab"])
    app.include_router(translate_router, prefix="/translate", tags=["translate"])

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/audio/{clip_id}", tags=["audio"])
    def serve_audio(clip_id: str, username: str = Depends(current_username)) -> FileResponse:
        path = audio_cache.get(clip_id)
        user = app_container.users().load(username)
        if path is None or user is None or not _user_owns_clip(user, clip_id):
            raise HTTPException(status_code=404, detail="Audio clip not found")
        return FileResponse(path, media_type="audio/mpeg")

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
