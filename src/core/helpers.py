import shutil
import tomllib
from contextlib import suppress
from datetime import date, datetime
from math import floor
from pathlib import Path
from sys import argv
from typing import Callable


__all__ = ["ALL_FILTERS", "ALL_MIDDLEWARE", "duration", "get_config", "make_dist"]


def get_config() -> dict[str, Path]:
    """Get the config JSON for the generator."""
    # Passing a path to the config toml file after the command will use that instead
    config_path = "config.toml"
    with suppress(IndexError):
        config_path = argv[1]

    config = tomllib.loads(Path(config_path).read_text())
    config["directories"] = {k: Path(v) for k, v in config["directories"].items()}
    return config


def make_dist() -> None:
    """Create all of the required directories."""
    config = get_config()
    dist_path: Path = config["directories"]["output"]

    # Delete any previous site generation first
    if dist_path.exists():
        shutil.rmtree(dist_path)

    # Create the directory the notes live in
    (dist_path / config["directories"]["post_output_base_slug"]).mkdir(parents=True, exist_ok=True)

    # Create the images directory
    (dist_path / "images").mkdir(parents=True, exist_ok=True)

    # Create the site static files folders and files
    shutil.copytree(config["directories"]["static"], (dist_path / "static"), dirs_exist_ok=True)


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
