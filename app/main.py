# from fastapi import FastAPI

# from app.core.config import settings
# from app.core.logging import configure_logging, get_logger
# from app.api.v1 import auth
# from app.api.v1 import users
# from app.api.v1 import organizations
# from app.api.v1 import teams
# from app.api.v1 import projects
# from app.api.v1 import task_statuses, tasks
# from app.api.v1 import attachments, comments
# from app.api.v1 import activity_logs, notifications
# from app.api.v1 import dashboard
# from app.middleware.rate_limit import RateLimitMiddleware
# from app.middleware.request_logging import RequestLoggingMiddleware
# from app.core.exception_handlers import register_exception_handlers

# configure_logging()

# logger = get_logger(__name__)


# def create_app() -> FastAPI:
#     app = FastAPI(
#         title=settings.APP_NAME,
#         debug=settings.DEBUG,
#         openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
#         docs_url=f"{settings.API_V1_PREFIX}/docs",
#     )

#     register_exception_handlers(app)

#     app.add_middleware(RateLimitMiddleware)
#     app.add_middleware(RequestLoggingMiddleware)
#     # Routers, middleware, and exception handlers will be registered here
#     # as they're built — empty at this stage of the roadmap.
#     app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(users.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(organizations.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(teams.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(projects.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(task_statuses.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(comments.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(attachments.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(activity_logs.router, prefix=settings.API_V1_PREFIX)

#     app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)

#     logger.info("Application configured", extra={"env": settings.APP_ENV})
#     return app


# app = create_app()


# @app.get("/health", tags=["health"])
# def health_check() -> dict[str, str]:

#     return {"status": "ok", "app": settings.APP_NAME}


from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.api.v1 import auth
from app.api.v1 import users
from app.api.v1 import organizations
from app.api.v1 import teams
from app.api.v1 import projects
from app.api.v1 import task_statuses, tasks
from app.api.v1 import attachments, comments
from app.api.v1 import activity_logs, notifications
from app.api.v1 import dashboard
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.core.exception_handlers import register_exception_handlers

from fastapi.staticfiles import StaticFiles
from app.web.routes import auth as web_auth
from app.web.routes import dashboard as web_dashboard
from app.web.routes import organizations as web_organizations
from app.web.routes import teams as web_teams
from app.web.routes import projects as web_projects
from app.web.routes import tasks as web_tasks
from app.web.routes import notifications as web_notifications

configure_logging()

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
    )

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    register_exception_handlers(app)

    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    # Routers, middleware, and exception handlers will be registered here
    # as they're built — empty at this stage of the roadmap.
    app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

    app.include_router(users.router, prefix=settings.API_V1_PREFIX)

    app.include_router(organizations.router, prefix=settings.API_V1_PREFIX)

    app.include_router(teams.router, prefix=settings.API_V1_PREFIX)

    app.include_router(projects.router, prefix=settings.API_V1_PREFIX)

    app.include_router(task_statuses.router, prefix=settings.API_V1_PREFIX)

    app.include_router(tasks.router, prefix=settings.API_V1_PREFIX)

    app.include_router(comments.router, prefix=settings.API_V1_PREFIX)

    app.include_router(attachments.router, prefix=settings.API_V1_PREFIX)

    app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)

    app.include_router(activity_logs.router, prefix=settings.API_V1_PREFIX)

    app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)

    app.include_router(web_auth.router)

    app.include_router(web_dashboard.router)

    app.include_router(web_organizations.router)

    app.include_router(web_teams.router)

    app.include_router(web_projects.router)

    app.include_router(web_tasks.router)

    app.include_router(web_notifications.router)

    logger.info("Application configured", extra={"env": settings.APP_ENV})
    return app


app = create_app()


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:

    return {"status": "ok", "app": settings.APP_NAME}
