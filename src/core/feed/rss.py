from datetime import UTC, datetime, time

from feedgen.feed import FeedGenerator

from src.app import config


__all__ = ["generate_rss_feed"]


def generate_rss_feed(all_posts: dict, /) -> bytes:
    """Generate a RSS feed of posts."""
    # Get the site config info we need
    site_meta = config.get("site")
    global_post_meta = config.get("post")

    # Define the base information
    fg = FeedGenerator()
    fg.id(site_meta["domain"])
    fg.title(site_meta["title"])
    fg.subtitle(site_meta["subtitle"])
    fg.link(href=site_meta["domain"], rel="self")
    fg.language("en-US")
    fg.logo(f"{site_meta['domain']}/static/favicon.png")

    # Add the default author's name if present
    if "author" in global_post_meta["defaults"]:
        fg.author({"name": global_post_meta["defaults"]["author"]})

    # List the most recent 5 posts available
    for post in tuple(all_posts.values())[:5]:
        fe = fg.add_entry(order="append")
        fe.id(post.meta["slug"])
        fe.link(href=f"{site_meta['domain']}{post.meta['url']}")
        fe.title(post.meta["title"])
        fe.published(datetime.combine(post.meta["date"], time.min).replace(tzinfo=UTC).isoformat())
    return fg.rss_str()
