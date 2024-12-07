import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import minify_html

from .app import config, current_app
from .core.helpers import remove_falsey_items, replace_curly_quotes


__all__ = ["Post", "PostIndex"]


@dataclass(slots=True)
class Page:
    file: Path
    content: str = ""
    raw_meta: str = ""
    template_key: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Make the model file point to the actual template name
        if not self.file.is_file():
            self.file = self.file / self.template_name
        self.from_file()

    @property
    def template_name(self) -> str:
        return config.get("site")["pages"][self.template_key]

    def from_file(self) -> None:
        """Read a page's content into memory."""
        self.content = replace_curly_quotes(self.file.read_text(encoding="utf-8"))

    def to_html(self, /, ctx: dict[str, Any] | None = None) -> str:
        """Render a page's content to a complete HTML page."""
        if ctx is None:
            ctx = {}
        return current_app()["render"]["jinja"].get_template(self.template_name).render(ctx)

    @staticmethod
    def to_file(path: Path, content: str) -> None:
        """Write a page to disk, optionally minifying it."""
        content = minify_html.minify(content) if config.get("minify") else content
        path.write_bytes(content.encode())


class Post(Page):
    """Represent an individual post."""

    parsed_content = None

    def __post_init__(self) -> None:
        # Extract the meta content from the page content,
        # then remove it because we don't want it in the content
        super().__post_init__()
        self.parse_content()
        self.parse_meta()
        self.generate_slug()
        self.generate_url()
        self.content = self.content.replace(self.raw_meta, "").strip()

    @property
    def template_name(self) -> str:
        return config.get("post")["post_template"]

    def from_markdown(self, /, ctx: dict[str, Any]) -> None:
        """Convert the page content from Markdown to HTML."""
        # `ctx` is provided to add the `wordcount` info to the post meta
        self.content = current_app()["render"]["markdown"].render(self.content, ctx)

    def generate_slug(self) -> None:
        """Generate a slug for this post."""
        self.meta["slug"] = quote_plus(
            "-".join(
                m.lower()
                for m in re.findall(r"\w+", self.meta["title"].replace("'", ""), flags=re.I)
            )
        )

    def generate_url(self) -> None:
        """Generate a URL for this post."""
        self.meta["url"] = "/{}/{}".format(str(config.get("post")["output_dir"]), self.meta["slug"])

    def parse_content(self) -> None:
        # Parse the content of the markdown file and store the AST for later
        # for further transformations
        self.parsed_content = current_app()["render"]["markdown"].parse(self.content)

    def parse_meta(self) -> None:
        """Extract a post's metadata from the file."""

        # Attempt to find the meta info
        if not (front_matter := [e for e in self.parsed_content if e.type == "front_matter"]):
            raise RuntimeError(f"Post {self.file.name} is missing meta")

        # Convert some data into native objects/and fill in default values to make things nicer
        page_meta = tomllib.loads(front_matter[0].content)
        page_meta["subtitle"] = page_meta.get(
            "subtitle", config.get("post")["defaults"]["subtitle"]
        )

        # If there is an author for the post, use it. Even if not, set the key
        page_meta["author"] = page_meta.get("author", "")

        # If there's no post author but a default author, use it instead
        default_author: str = config.get("post")["defaults"].get("author", "")
        if not page_meta["author"] and default_author:
            page_meta["author"] = default_author

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

        # Create a container for the post reading stats
        page_meta["wordcount"] = {}

        # Generate the caption for the featured image for the post if the both exist
        if page_meta.get("image") and page_meta.get("caption"):
            page_meta["caption"] = current_app()["render"]["markdown"].render(page_meta["caption"])

        # Store the meta info, both parsed and raw text
        self.meta = page_meta
        self.raw_meta = front_matter[0].content


class PostIndex(Page):
    """Represent the post index page post."""

    @property
    def template_name(self) -> str:
        return config.get("post")["index_template"]
