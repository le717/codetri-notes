import configparser
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

from jinja2 import Environment, PackageLoader, select_autoescape

from src.core import helpers, page


__all__ = ["main"]


def _format_dt(dt: datetime, fmt: str) -> str:
    """Format a datetime object to a datestring."""
    if fmt == "iso":
        return dt.isoformat()
    return dt.strftime(fmt)


def main():
    # Start by creating a Jinja2 renderer and adding all our custom middleware and filters
    env = Environment(
        loader=PackageLoader("src", "templates"),
        autoescape=select_autoescape(["html"]),
    )
    env.globals.update(helpers.ALL_MIDDLEWARE)
    env.filters.update(helpers.ALL_FILTERS)

    # Get the generator config
    config = helpers.get_config()

    # Create the output directory
    config["note_path"].mkdir(parents=True, exist_ok=True)

    # Get the templates
    template_index = (config["templates"] / "index.jinja2").read_text()
    template_note = (config["templates"] / "note.jinja2").read_text()

    # Generate each note
    all_notes = []
    for f in config["input"].iterdir():
        # Get the note content and metadata
        content = f.read_text()
        meta = page.meta(content)

        # Remove the raw meta from the note
        content = content.replace(meta["raw_text"], "").strip()

        # Convert the publish date to a datetime object for better usage
        date = datetime.fromisoformat(meta["date"])

        # Fill in all the content
        render_opts = {
            "title": meta["title"],
            "content": content,
            "date_published": date,
            "date_format": config["date_format"],
        }
        rendered_note = page.render("note", render_opts, env)

        # Keep a record of the note so we can generate the index when we are done
        note_file = f"{quote_plus(meta['url'])}.html"
        all_notes.append({"title": meta["title"], "date": date, "url": note_file})

        # Write the generated note
        page.write(note_file, data=rendered_note)

    # Sort all of the notes, with the newest on top
    all_notes.sort(key=lambda x: x["date"], reverse=True)

    # Generate the HTML list of all notes for the index
    html = []
    for note in all_notes:
        html.append("<li>")
        html.append(
            '<a href="note/{url}">{title} ({date})</a>'.format(
                url=note["url"],
                title=note["title"],
                date=_format_dt(note["date"], config["date_format"]),
            )
        )
        html.append("</li>")
    html = "".join(html)

    # Write the index
    index_content = re.sub("<!--notes-->", html, template_index)
    (config["output"] / "index.html").write_text(index_content)


if __name__ == "__main__":
    main()
