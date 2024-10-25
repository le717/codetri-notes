from configparser import ConfigParser
from pathlib import Path

import minify_html
from jinja2 import Environment


__all__ = ["meta", "render", "write"]


def meta(content: str, /) -> dict:
    """Extract a note's metadata."""
    # Use the Python `configparser` for quickness for note metadata
    parser = ConfigParser(default_section="meta")

    # Get the metadata
    end_tag = "[endmeta]"
    raw_text = content[: content.find(end_tag) + len(end_tag)]
    parser.read_string(raw_text)

    # Pull the metadata out of the base key and append the raw text
    note_meta = parser["meta"]
    note_meta["raw_text"] = raw_text
    parser.clear()
    return note_meta


def render(
    template: str,
    render_opts: dict,
    jinja: Environment,
) -> str:
    template = jinja.get_template(f"{template}.jinja2")
    return template.render(**render_opts)


def write(*path: str, data: str = "", should_minify: bool = False) -> None:
    minfied_data = minify_html.minify(data) if should_minify else data
    (Path().joinpath(*path)).write_bytes(minfied_data.encode())
