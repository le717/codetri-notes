from contextvars import ContextVar
from typing import Any


APP_CONFIG: ContextVar[dict[str, dict[str, Any]]] = ContextVar("config", default={})


__all__ = ["set_initial", "get"]


def get(key: str) -> Any:
    config = APP_CONFIG.get()
    return config[key]


def set_initial(data: dict[str, Any]) -> None:
    APP_CONFIG.set(data)
