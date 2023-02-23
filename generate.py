from datetime import datetime
from urllib.parse import quote_plus

from jinja2 import Environment, PackageLoader, select_autoescape

from src.core import helpers, page


__all__ = ["main"]


def main():
    # Start by creating a Jinja2 renderer and adding all
    # our custom middleware and filters
    env = Environment(
        loader=PackageLoader("usr", "templates"),
        autoescape=select_autoescape(["html"]),
    )
    env.globals.update(helpers.ALL_MIDDLEWARE)
    env.filters.update(helpers.ALL_FILTERS)

    # Get the generator config and set up for dist
    config = helpers.get_config()
    helpers.make_dist()

    # Generate each note
    all_notes = []
    for f in config["paths"]["input"].iterdir():
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
        page.write(
            config["paths"]["output"],
            config["paths"]["note_path"],
            note_file,
            data=rendered_note,
        )

    # Sort all of the notes, with the newest on top
    all_notes.sort(key=lambda x: x["date"], reverse=True)

    # Build up the index with all the current notes
    render_opts = {
        "notes": all_notes,
        "date_format": config["date_format"],
    }
    rendered_index = page.render("index", render_opts, env)
    page.write(config["paths"]["output"], "index.html", data=rendered_index)


if __name__ == "__main__":
    main()
