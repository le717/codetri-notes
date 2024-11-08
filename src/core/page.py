from configparser import ConfigParser
from pathlib import Path

import minify_html
from jinja2 import Environment


__all__ = ["meta", "render", "replace_curly_quotes", "write"]


def meta(content: str, /) -> dict[str, str]:
    """Extract a note's metadata."""
    # Use the Python `configparser` for quickness for note metadata
    parser = ConfigParser(default_section="meta")

    # Get the metadata
    start_tag = "[meta]"
    end_tag = "[endmeta]"
    raw_text = content[content.find(start_tag) : content.find(end_tag) + len(end_tag)]
    parser.read_string(raw_text)

    # Pull the metadata out of the base key and append the raw text
    note_meta = parser["meta"]
    note_meta["raw_text"] = raw_text
    parser.clear()
    return note_meta


def render(template: str, render_opts: dict, jinja: Environment) -> str:
    template = jinja.get_template(f"{template}.jinja2")
    return template.render(**render_opts)


def replace_curly_quotes(text: str) -> str:
    """Replace any curly quotes in the text with straight quotes."""
    return text.replace("“", '"').replace("”", '"').replace("’", "'")


def write(*path: str, data: str = "", should_minify: bool = False) -> None:
    minfied_data = minify_html.minify(data) if should_minify else data
    (Path().joinpath(*path)).write_bytes(minfied_data.encode())
