import argparse
import re
import tomllib
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import time
from urllib.parse import quote_plus

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.wordcount import wordcount_plugin

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
    parser.add_argument(
        "-m",
        "--minify",
        action="store_true",
        help="Should the generated files be minified? (default: no)",
    )
    parsed = parser.parse_args()

    # Display the argument values used
    print("Executing with the following arguments:")
    for a in parser._actions:
        with suppress(AttributeError):
            print(f"\t* {a.dest}={getattr(parsed, a.dest)}")
    return parsed


def main() -> None:
    # Get the current time for a bit of info about runtime
    start_time = time()

    # Resolve the config file we are to use and load the contents therein
    args = get_arguments()
    config.set_initial(Path(args.config))

    # Start by creating a Jinja2 renderer and adding all our custom middleware and filters
    env = Environment(
        loader=FileSystemLoader(config.get("directories")["theme"]),
        autoescape=select_autoescape(["html"]),
    )
    env.globals.update(helpers.ALL_MIDDLEWARE)
    env.filters.update(helpers.ALL_FILTERS)

    # Create our markdown -> html renderer
    md_renderer = MarkdownIt("gfm-like").use(front_matter_plugin).use(wordcount_plugin)
    md_renderer.options["xhtmlOut"] = False

    # Create all of the directories that we need for dist
    helpers.make_dist()

    # Generate each note
    all_notes = []
    for f in config.get("directories")["posts"].iterdir():
        # Filter out dot files
        if f.name.startswith("."):
            continue

        # Get the note content and metadata
        content = f.read_text(encoding="utf-8")
        meta = page.meta(content)

        # Remove the raw meta from the note
        content = content.replace(meta["raw_text"], "").strip()

        # Convert the publish date to a datetime object for better usage
        date = datetime.fromisoformat(meta["date"])

        # Fill in all the content
        render_opts = {
            "site": config.get("site"),
            "post": {
                "title": meta["title"],
                "subtitle": meta.get("subtitle", config.get("post")["defaults"]["subtitle"]),
                "author": meta.get("author", config.get("post")["defaults"]["author"]),
                "content": content,
                "date_published": date,
            },
            # Populated by markdown parser for nice "read time" stats
            # TODO: Have wordcount saved into page meta
            "wordcount": {},
        }

        # If we have encountered a Markdown file, we need to render it to HTML first
        # TODO: Highly considering only supporting markdown files for posts
        if f.suffix == ".md":
            # TODO: Update all posts to use front-matter and toml for meta
            if new_meta := [e for e in md_renderer.parse(content) if e.type == "front_matter"]:
                parsed_new_meta = tomllib.loads(new_meta[0].content)
            render_opts["post"]["content"] = md_renderer.render(content, render_opts)

        # Render the page with the post content
        rendered_note = page.render("post", render_opts, env)

        # Automatically generate a slug from the post title
        slug = "-".join(m.lower() for m in re.findall(r"\w+", meta["title"], flags=re.I))

        # Keep a record of the note so we can generate the index when we are done
        note_file = f"{quote_plus(slug)}.html"
        all_notes.append({
            "title": meta["title"],
            "subtitle": meta.get("subtitle", config.get("post")["defaults"]["subtitle"]),
            "author": meta.get("author", config.get("post")["defaults"]["author"]),
            "date": date,
            "url": "{}/{}".format(
                str(config.get("directories")["post_output_base_slug"]), note_file
            ),
        })

        # Write the generated note
        page.write(
            str(config.get("directories")["output"]),
            str(config.get("directories")["post_output_base_slug"]),
            note_file,
            data=rendered_note,
            should_minify=args.minify,
        )

    # Sort all of the notes, with the newest on top
    all_notes.sort(key=lambda x: x["date"], reverse=True)

    # Build up the index with all the current notes
    render_opts = {
        "posts": all_notes,
        "site": config.get("site"),
        "post": {"title": "Home"},
    }
    rendered_index = page.render("index", render_opts, env)
    page.write(
        str(config.get("directories")["output"]),
        "index.html",
        data=rendered_index,
        should_minify=args.minify,
    )

    # Provide a basic "how long did it run" message
    total_time = time() - start_time
    print(f"Total generation time: {helpers.duration(total_time)}")


if __name__ == "__main__":
    main()
