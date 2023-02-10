from datetime import date, datetime
import json
from pathlib import Path
from typing import Callable

__all__ = ["ALL_FILTERS", "ALL_MIDDLEWARE", "get_config"]


def get_config() -> dict[str, Path]:
    """Get the config JSON for the generator."""
    config = json.loads(Path("config.json").read_text())
    not_paths = ["date_format", "paths"]
    config = {k: Path(v) if k not in not_paths else v for k, v in config.items()}
    config["note_path"] = config["output"] / config["note_path"]
    return config


def current_year() -> int:
    """Get the current year."""
    return date.today().year


def format_datetime(dt: datetime, fmt: str) -> str:
    """Format a datetime object to a datestring."""
    if fmt == "iso":
        return dt.isoformat()
    return dt.strftime(fmt)


ALL_FILTERS = {}
ALL_MIDDLEWARE: dict[str, Callable] = {
    "current_year": current_year(),
    "format_datetime": format_datetime,
}
