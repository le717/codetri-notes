import argparse
from contextlib import suppress
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.wordcount import wordcount_plugin

from ..core import helpers
from . import config, render_rules


APP: ContextVar[dict[str, dict[str, Any]]] = ContextVar("app", default={})


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
    parser.add_argument(
        "--no-feed",
        action="store_true",
        help="Disable generating RSS and JSON feed files (default: no)",
    )
    args = parser.parse_args()

    # Display the argument values used
    print("Executing with the following arguments:")
    for a in parser._actions:
        with suppress(AttributeError):
            print(f"\t* {a.dest}={getattr(args, a.dest)}")
    return args


def create_app() -> dict[str, dict[str, Any]]:
    # Get the arguments the script was invoked with and set up the app config
    args = get_arguments()
    config.set_initial(Path(args.config))
    config.set("minify", args.minify)
    config.set("feed", not args.no_feed)

    # Create our markdown -> html renderer
    markdown = MarkdownIt("gfm-like").use(front_matter_plugin).use(wordcount_plugin)
    markdown.options["xhtmlOut"] = False
    markdown.add_render_rule("link_open", render_rules.render_link_open)
    markdown.add_render_rule("image", render_rules.render_image_caption)

    # Create our jinja2 html renderer
    jinja = Environment(
        loader=FileSystemLoader(config.get("directories")["theme"]),
        autoescape=select_autoescape(["html"]),
    )
    jinja.globals.update(helpers.ALL_GLOBALS)
    jinja.globals.update({"site": config.get("site")})
    jinja.filters.update(helpers.ALL_FILTERS)

    # Put everything together
    app = current_app()
    app["render"] = {"markdown": markdown, "jinja": jinja}
    APP.set(app)
    return app


def current_app() -> dict[str, dict[str, Any]]:
    return APP.get()
