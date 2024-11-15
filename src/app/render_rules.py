_all__ = ["render_link_open"]


def render_link_open(self, tokens, idx, options, env):
    """Add render rule for `link_open`."""
    # Add "don't track" signals to an `<a>` tag
    tokens[idx].attrSet("rel", "noopener noreferrer")

    # If the link target is an internal link, indicated by a markdown file name,
    # replace it with the generated slug
    # TODO: Fill this in alongside generate2
    # if tokens[idx].attrs["href"] in ...: ...

    return self.renderToken(tokens, idx, options, env)
