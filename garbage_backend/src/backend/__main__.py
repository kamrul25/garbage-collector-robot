"""Entry point: uv run backend"""
import uvicorn

from backend.config import settings
from backend.main import create_app


def main():
    app = create_app()
    uvicorn.run(app, host=settings.server.host, port=settings.server.port)

if __name__ == "__main__":
    main()   