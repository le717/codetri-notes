import shutil
import tomllib
from datetime import date, datetime
from math import floor
from pathlib import Path
from typing import Callable

from src.core import config


__all__ = ["ALL_FILTERS", "ALL_MIDDLEWARE", "duration", "set_config_data", "make_dist"]


def set_config_data(config_file: str) -> dict[str, Path]:
    """Get the config TOML for the generator."""
    data = tomllib.loads(Path(config_file).read_text())
    data["directories"] = {k: Path(v) for k, v in data["directories"].items()}
    config.set_initial(data)


def make_dist() -> None:
    """Create all of the required directories."""
    all_directories: dict[str, Path] = config.get("directories")
    dist_path: Path = all_directories["output"]

    # Delete any previous site generation first
    if dist_path.exists():
        shutil.rmtree(dist_path)

    # Create the directory the notes live in
    (dist_path / all_directories["post_output_base_slug"]).mkdir(parents=True, exist_ok=True)

    # Create the media directory
    shutil.copytree(
        all_directories["media"], (dist_path / all_directories["media"].stem), dirs_exist_ok=True
    )

    # Create the site static files folders and files
    shutil.copytree(all_directories["static"], (dist_path / "static"), dirs_exist_ok=True)


def current_year() -> int:
    """Get the current year."""
    return date.today().year


def format_datetime(dt: datetime, fmt: str) -> str:
    """Format a datetime object to a datestring."""
    if fmt == "iso":
        return dt.isoformat()
    return dt.strftime(fmt)


def duration(seconds: int) -> str:
    # https://stackoverflow.com/a/3856312
    hours = floor(seconds / 3600)
    mins = floor(seconds / 60 % 60)
    secs = floor(seconds % 60)

    # Only display the hours if needed
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


ALL_FILTERS = {}
ALL_MIDDLEWARE: dict[str, Callable] = {
    "current_year": current_year(),
    "format_datetime": format_datetime,
}
