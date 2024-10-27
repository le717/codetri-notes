import tomllib
from contextvars import ContextVar
from pathlib import Path
from typing import Any


APP_CONFIG: ContextVar[dict[str, dict[str, Any]]] = ContextVar("config", default={})


__all__ = ["set_initial", "get"]


def get(key: str) -> Any:
    config = APP_CONFIG.get()
    return config[key]


def set_initial(config_file: Path) -> None:
    data = tomllib.loads(config_file.read_text())

    # Convert all directory paths to actual Path objects before saving for direct usage
    data["directories"] = {k: Path(v) for k, v in data["directories"].items()}

    APP_CONFIG.set(data)
