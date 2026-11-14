"""Logging setup."""
import logging
import sys
from pathlib import Path

from backend.config import settings


def setup_logging():
    level = getattr(logging, settings.logging.level.upper(), logging.INFO)
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if settings.logging.file:
        log_path = Path(settings.logging.file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path))

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )   