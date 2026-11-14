"""FastAPI application factory."""
from fastapi import FastAPI

from backend.api.routes import router
from backend.services.controller import start_control_loop, stop_control_loop
from backend.utils.logger import setup_logging


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title="Garbage Collector Backend",
        version="0.1.0",
        docs_url="/docs",
    )
    app.include_router(router)

    @app.on_event("startup")
    async def on_startup():
        start_control_loop(app)

    @app.on_event("shutdown")
    async def on_shutdown():
        stop_control_loop(app)

    return app   