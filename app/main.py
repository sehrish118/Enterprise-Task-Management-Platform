from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.api.v1 import auth
from app.api.v1 import users
from app.api.v1 import organizations
from app.api.v1 import teams
from app.api.v1 import projects
from app.api.v1 import task_statuses, tasks
# ...

configure_logging()

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
    )

    # Routers, middleware, and exception handlers will be registered here
    # as they're built — empty at this stage of the roadmap.
    app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

    app.include_router(users.router, prefix=settings.API_V1_PREFIX)

    app.include_router(organizations.router, prefix=settings.API_V1_PREFIX)

    app.include_router(teams.router, prefix=settings.API_V1_PREFIX)

    app.include_router(projects.router, prefix=settings.API_V1_PREFIX)

    app.include_router(task_statuses.router, prefix=settings.API_V1_PREFIX)
    app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)

    logger.info("Application configured", extra={"env": settings.APP_ENV})
    return app


app = create_app()


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:

    return {"status": "ok", "app": settings.APP_NAME}
