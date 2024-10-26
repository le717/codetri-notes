import html

from mistletoe.html_renderer import HtmlRenderer
from mistletoe.span_token import Image


__all__ = ["CodeTriRenderer"]


class CodeTriRenderer(HtmlRenderer):
    def render_image(self, token: Image) -> str:
        template = """<figure>
            <img src="{src}" alt="{alt}">
            <figcaption>{caption}</figcaption>
        </figure>"""

        alt = html.escape(token.title) if token.title else ""

        return template.format(src=token.src, caption=self.render_to_plain(token), alt=alt)
