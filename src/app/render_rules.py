__all__ = ["render_image_caption", "render_link_open"]


def render_image_caption(self, tokens, idx: int, options, env):
    # If there's no alt text, render as normal
    if tokens[0].children is None:
        return self.image(tokens, idx, options, env)

    # Overload the alt text to generate a figure and with caption
    caption = self.renderInline(tokens[0].children, options, env)
    img_tag = self.image(tokens, idx, options, env)
    return f"<figure>{img_tag}<figcaption>{caption}</figcaption></figure>"


def render_link_open(self, tokens, idx: int, options, env):
    """Add render rule for `link_open`."""
    # Add "don't track" signals to an `<a>` tag
    tokens[idx].attrSet("rel", "noopener noreferrer")

    # When possible, if the link target is an internal link, indicated by a markdown file name,
    # replace it with the generated slug
    if "all_urls" in env and tokens[idx].attrs["href"] in env["all_urls"]:
        tokens[idx].attrs["href"] = env["all_urls"][tokens[idx].attrs["href"]]
    return self.renderToken(tokens, idx, options, env)
