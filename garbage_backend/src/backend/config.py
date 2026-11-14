"""Load and expose application settings from YAML + env overrides."""
import os
from pathlib import Path

import yaml
from pydantic import BaseModel


# ─── Pydantic models for type-safe config ───────────────────
class CameraConfig(BaseModel):
    ip: str
    stream_url: str
    resolution: tuple[int, int]

class DevKitConfig(BaseModel):
    ip: str
    port: int
    cmd_url: str

class ModelConfig(BaseModel):
    path: str
    confidence: float
    target_classes: list[str]

class DecisionConfig(BaseModel):
    center_tolerance: float
    stop_distance_cm: int
    approach_speed: int
    turn_speed: int
    seek_speed: int

class ServerConfig(BaseModel):
    host: str
    port: int
    fps_limit: int

class LoggingConfig(BaseModel):
    level: str
    file: str | None = None

class Settings(BaseModel):
    camera: CameraConfig
    devkit: DevKitConfig
    model: ModelConfig
    decision: DecisionConfig
    server: ServerConfig
    logging: LoggingConfig

def _load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def get_settings(config_path: str | None = None) -> Settings:
    """Load settings. Override with env vars if set (e.g. CAM_IP)."""
    if config_path is None:
        # Walk up from this file to find config/
        base = Path(__file__).resolve().parent.parent.parent
        config_path = base / "config" / "settings.yaml"

    raw = _load_yaml(Path(config_path))

    # Optional env overrides
    if os.getenv("CAM_IP"):
        raw["camera"]["ip"] = os.getenv("CAM_IP")
        raw["camera"]["stream_url"] = f"http://{os.getenv('CAM_IP')}/stream"
    if os.getenv("DEVKIT_IP"):
        raw["devkit"]["ip"] = os.getenv("DEVKIT_IP")
        raw["devkit"]["cmd_url"] = f"http://{os.getenv('DEVKIT_IP')}:{raw['devkit']['port']}/cmd"

    return Settings(**raw)

# Singleton (imported everywhere)
settings = get_settings()   