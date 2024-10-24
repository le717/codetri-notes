import argparse
from datetime import datetime
from pathlib import Path
from time import time
from urllib.parse import quote_plus

import mistletoe
from jinja2 import Environment, FileSystemLoader, select_autoescape
from mistletoe.contrib.github_wiki import GithubWikiRenderer

from src.core import config, helpers, page


__all__ = ["main"]


def get_arguments() -> argparse.Namespace:
    """Add command-line arguments to the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        default="config.toml",
        help="Specify the config TOML file to use when building the site.",
    )
    return parser.parse_args()


def main() -> None:
    # Get the current time for a bit of info about runtime
    start_time = time()

    # Resolve the config file we are to use and load the contents therein
    args = get_arguments()
    print(Path(args.config))
    helpers.set_config_data(args.config)

    # Start by creating a Jinja2 renderer and adding all our custom middleware and filters
    env = Environment(
        loader=FileSystemLoader(config.get_value("directories")["theme"]),
        autoescape=select_autoescape(["html"]),
    )
    env.globals.update(helpers.ALL_MIDDLEWARE)
    env.filters.update(helpers.ALL_FILTERS)

    # Create all of the directories that we need for dist
    helpers.make_dist()

    # Generate each note
    all_notes = []
    for f in config.get_value("directories")["posts"].iterdir():
        # Filter out dot files
        if f.name.startswith("."):
            continue

        # Get the note content and metadata
        content = f.read_text()
        meta = page.meta(content)

        # Remove the raw meta from the note
        content = content.replace(meta["raw_text"], "").strip()

        # Convert the publish date to a datetime object for better usage
        date = datetime.fromisoformat(meta["date"])

        # Fill in all the content
        render_opts = {
            "site": config.get_value("site"),
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
            "url": "{}/{}".format(
                str(config.get_value("directories")["post_output_base_slug"]), note_file
            ),
        })

        # Write the generated note
        page.write(
            str(config.get_value("directories")["output"]),
            str(config.get_value("directories")["post_output_base_slug"]),
            note_file,
            data=rendered_note,
        )

    # Sort all of the notes, with the newest on top
    all_notes.sort(key=lambda x: x["date"], reverse=True)

    # Build up the index with all the current notes
    render_opts = {
        "posts": all_notes,
        "site": config.get_value("site"),
        "post": {"title": "Home"},
    }
    rendered_index = page.render("index", render_opts, env)
    page.write(str(config.get_value("directories")["output"]), "index.html", data=rendered_index)

    # Provide a basic "how long did it run" message
    total_time = time() - start_time
    print(f"Total generation time: {helpers.duration(total_time)}")


if __name__ == "__main__":
    main()
