from pathlib import Path

import minify_html
from jinja2 import Environment


__all__ = ["render", "write"]


def render(template: str, render_opts: dict, jinja: Environment) -> str:
    template = jinja.get_template(f"{template}.jinja2")
    return template.render(**render_opts)


def write(*path: str, data: str = "", should_minify: bool = False) -> None:
    minfied_data = minify_html.minify(data) if should_minify else data
    (Path().joinpath(*path)).write_bytes(minfied_data.encode())
