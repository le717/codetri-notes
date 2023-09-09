import shutil
import tomllib
from datetime import date, datetime
from pathlib import Path
from typing import Callable

__all__ = ["ALL_FILTERS", "ALL_MIDDLEWARE", "get_config", "make_dist"]


def get_config() -> dict[str, Path]:
    """Get the config JSON for the generator."""
    config = tomllib.loads(Path("config.toml").read_text())
    config["directories"] = {k: Path(v) for k, v in config["directories"].items()}
    return config


def make_dist() -> None:
    """Create all of the required directories."""
    config = get_config()
    dist_path = Path(config["directories"]["output"])

    # TODO: Delete everything first

    # Create the directory the notes live in
    (dist_path / config["directories"]["posts"]).mkdir(parents=True, exist_ok=True)

    # Create the images directory
    (dist_path / "images").mkdir(parents=True, exist_ok=True)

    # Create the site static files folders and files
    src_path = (Path() / "static").as_posix()
    shutil.copytree(src_path, (dist_path / "static").as_posix(), dirs_exist_ok=True)


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
