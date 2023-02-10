import shutil
from pathlib import Path

from jinja2 import Environment

from src.core.helpers import get_config

__all__ = ["dist", "render", "write"]


# def dist(dir_names: list[str]) -> None:
#     dist_path = sys_vars.get_path("DIST_PATH")

#     # Create the film years folders
#     for dir_name in dir_names:
#         (dist_path / "films" / dir_name).mkdir(parents=True, exist_ok=True)

#     # Create the film images folder
#     (dist_path / "films" / "images").mkdir(parents=True, exist_ok=True)

#     # Create the site static files folders and files
#     src_path = (Path() / "src" / "static").as_posix()
#     shutil.copytree(src_path, dist_path.as_posix(), dirs_exist_ok=True)


def render(
    template: str,
    render_opts: dict,
    jinja: Environment,
) -> str:
    template = jinja.get_template(f"{template}.jinja2")
    return template.render(**render_opts)


def write(*path: str, data: str = ""):
    (get_config()["note_path"].joinpath(*path)).write_bytes(data.encode())
