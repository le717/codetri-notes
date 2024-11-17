_all__ = ["render_link_open"]


def render_link_open(self, tokens, idx, options, env):
    """Add render rule for `link_open`."""
    # Add "don't track" signals to an `<a>` tag
    tokens[idx].attrSet("rel", "noopener noreferrer")

    # When possible, if the link target is an internal link, indicated by a markdown file name,
    # replace it with the generated slug
    if "all_urls" in env and tokens[idx].attrs["href"] in env["all_urls"]:
        tokens[idx].attrs["href"] = env["all_urls"][tokens[idx].attrs["href"]]
    return self.renderToken(tokens, idx, options, env)
