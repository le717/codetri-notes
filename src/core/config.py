from contextvars import ContextVar
from typing import Any


APP_CONFIG: ContextVar[dict[str, dict[str, Any]]] = ContextVar("config", default={})


__all__ = ["set_config", "get_value"]


def get_value(key: str) -> Any:
    config = APP_CONFIG.get()
    return config[key]


def set_config(data: dict[str, Any]) -> None:
    APP_CONFIG.set(data)
