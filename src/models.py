import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import minify_html

from .app import config, current_app
from .core.helpers import remove_falsey_items


__all__ = ["Home", "Post", "PostIndex"]


@dataclass(slots=True)
class Page:
    file: Path
    title: str = ""
    content: str = ""
    slug: str = ""
    raw_meta: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.from_file()

    def _replace_curly_quotes(text: str) -> str:
        """Replace any curly quotes in the text with straight quotes."""
        return text.replace("“", '"').replace("”", '"').replace("’", "'")

    def from_file(self) -> None:
        """Read a page's content into memory."""
        self.content = self.file.read_text(encoding="utf-8")

    def to_html(self, ctx: dict) -> str:
        """Render a page's content to a complete HTML page."""
        return current_app()["renderers"]["jinja"].get_template(self.template_name).render(ctx)

    def to_file(self, path: Path) -> None:
        """Write a page to disk, optionally minifying it."""
        content = minify_html.minify(self.content) if config.get("minify") else self.content
        path.write_bytes(content.encode())


class Home(Page):
    """Represent the site home post."""


class Post(Page):
    """Represent an individual post."""

    parsed_content = None

    def __post_init__(self) -> None:
        # Extract the meta content from the page content,
        # then remove it because we don't want it in the content
        super().__post_init__()
        self.parse_meta()
        self.content = self._replace_curly_quotes(self.content.replace(self.raw_meta, "").strip())
        self.parse_content()

    @property
    def template_name(self) -> str:
        return config.get("post")["post_template"]

    def from_markdown(self) -> str:
        """Convert the page content from Markdown to HTML."""
        # `self.meta` is provided to add the `wordcount` info to the post meta
        return current_app()["renderers"]["markdown"].render(self.content, self.meta)

    def parse_content(self) -> None:
        # Parse the content of the markdown file and store the AST for later
        # for further transformations
        self.parsed_content = current_app()["renderers"]["markdown"].parse(self.content)

    def parse_meta(self) -> None:
        """Extract a post's metadata from the file."""

        # Attempt to find the meta info
        if not (front_matter := [e for e in self.parsed_content if e.type == "front_matter"]):
            raise RuntimeError("Post meta must be present")

        # Convert some data into native objects/and fill in default values to make things nicer
        page_meta = tomllib.loads(self._replace_curly_quotes(front_matter[0].content))
        page_meta["subtitle"] = page_meta.get(
            "subtitle", config.get("post")["defaults"]["subtitle"]
        )
        page_meta["author"] = page_meta.get("author", config.get("post")["defaults"]["author"])

        # If there are no tags for the post, set the key. If there are default tags, use them
        page_meta["tags"] = page_meta.get("tags", [])

        # If there are tags, and it's a single string value, wrap it in a list
        # for a consistent render context variable
        if isinstance(page_meta["tags"], str):
            page_meta["tags"] = [page_meta["tags"]]
        page_meta["tags"] = remove_falsey_items(page_meta["tags"])

        # Pull out any default post tags
        default_tags: str | list[str] = config.get("post")["defaults"].get("tags", [])
        default_tags_before: bool = config.get("post")["defaults"].get("tags_before", True)

        # If the default tags are just a string, wrap it in a list
        if isinstance(default_tags, str):
            default_tags = [default_tags]
        default_tags = remove_falsey_items(default_tags)

        # Order the default and specific are requested
        if default_tags_before:
            page_meta["tags"] = default_tags + page_meta["tags"]
        else:
            page_meta["tags"] = page_meta["tags"] + default_tags

        # Store the meta info, both parsed and raw text
        self.meta = page_meta
        self.raw_meta = self._replace_curly_quotes(front_matter[0].content)


class PostIndex(Page):
    """Represent the post index page post."""

    @property
    def template_name(self) -> str:
        return config.get("post")["index_template"]
