_all__ = ["render_link_no_tracking"]


def render_link_no_tracking(self, tokens, idx, options, env):
    """Add "don't track" signals to URLs."""
    tokens[idx].attrSet("rel", "noopener noreferrer")
    return self.renderToken(tokens, idx, options, env)
