import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.ai.vision.vision_classifier import get_vision_classifier
from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import install_exception_handlers
from app.core.logging import configure_logging, get_logger


configure_logging()
logger = get_logger("fitfuel.main")


def create_application() -> FastAPI:
    """
    Application factory.
    Keeps app creation clean and test-friendly.
    """
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.app_debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    install_exception_handlers(application)

    @application.on_event("startup")
    async def preload_vision_model() -> None:
        """
        Warm the vision model once at startup so the first inference request
        does not pay the full ResNet50 cold-start cost.
        """
        try:
            classifier = get_vision_classifier()
            classifier.warm_up()
            logger.info(
                "Vision classifier warmed successfully on startup. device=%s",
                settings.vision_device,
            )
        except Exception as exc:
            logger.warning(
                "Vision classifier warm-up skipped or failed: %s",
                str(exc),
            )

    @application.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        started_at = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)

        logger.info(
            "%s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    @application.get("/", tags=["Meta"])
    async def root() -> dict[str, str]:
        return {
            "message": f"{settings.app_name} is running.",
            "docs": "/docs",
            "health": f"{settings.api_v1_prefix}/health",
        }

    application.include_router(api_router, prefix=settings.api_v1_prefix)

    logger.info("Application created successfully.")
    return application


app = create_application()