from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import mistletoe
from jinja2 import Environment, PackageLoader, select_autoescape
from mistletoe.contrib.github_wiki import GithubWikiRenderer

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
    for f in (Path("usr") / "posts").iterdir():
        # Get the note content and metadata
        content = f.read_text()
        meta = page.meta(content)

        # Remove the raw meta from the note
        content = content.replace(meta["raw_text"], "").strip()

        # Convert the publish date to a datetime object for better usage
        date = datetime.fromisoformat(meta["date"])

        # Fill in all the content
        render_opts = {
            "site": config["site"],
            "post": {
                "title": meta["title"],
                "content": content,
                "date_published": date,
            },
        }

        # If we have encountered a Markdown file, we need to render it to HTML first
        if f.suffix == ".md":
            render_opts["post"]["content"] = mistletoe.markdown(content, GithubWikiRenderer)

        # Render the page with the post content
        rendered_note = page.render("post", render_opts, env)

        # Keep a record of the note so we can generate the index when we are done
        note_file = f"{quote_plus(meta['url'])}.html"
        all_notes.append({
            "title": meta["title"],
            "date": date,
            "url": "{}/{}".format(config["directories"]["posts"], note_file),
        })

        # Write the generated note
        page.write(
            config["directories"]["output"],
            config["directories"]["posts"],
            note_file,
            data=rendered_note,
        )

    # Sort all of the notes, with the newest on top
    all_notes.sort(key=lambda x: x["date"], reverse=True)

    # Build up the index with all the current notes
    render_opts = {
        "posts": all_notes,
        "site": config["site"],
        "post": {"title": "Home"},
    }
    rendered_index = page.render("index", render_opts, env)
    page.write(config["directories"]["output"], "index.html", data=rendered_index)


if __name__ == "__main__":
    main()
