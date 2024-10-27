import tomllib
from contextvars import ContextVar
from pathlib import Path
from typing import Any


APP_CONFIG: ContextVar[dict[str, dict[str, Any]]] = ContextVar("config", default={})


__all__ = ["get", "set", "set_initial"]


def get(key: str) -> Any:
    config = APP_CONFIG.get()
    return config[key]


def set(key: str, value: Any) -> None:
    config = APP_CONFIG.get()
    config[key] = value
    APP_CONFIG.set(config)


def set_initial(config_file: Path) -> None:
    data = tomllib.loads(config_file.read_text())

    # Convert all directory paths to actual Path objects before saving for direct usage
    data["directories"] = {k: Path(v) for k, v in data["directories"].items()}

    APP_CONFIG.set(data)
