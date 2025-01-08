import json
from datetime import UTC, datetime, time

from src.app import config


__all__ = ["generate_json_feed"]


def generate_json_feed(all_posts: dict, /) -> str:
    """Generate a JSON feed of posts.

    https://www.jsonfeed.org/
    """
    # Get the site config info we need
    site_meta = config.get("site")
    global_post_meta = config.get("post")

    # Define the base information
    feed = {
        "version": "https://www.jsonfeed.org/version/1.1/",
        "title": site_meta["title"],
        "description": site_meta["subtitle"],
        "home_page_url": site_meta["domain"],
        "feed_url": f"{site_meta['domain']}/feed.json",
        "language": "en-US",
        "icon": f"{site_meta['domain']}/static/logo.svg",
        "favicon": f"{site_meta['domain']}/static/favicon.png",
    }

    # Add the default author's name if present
    if "author" in global_post_meta["defaults"]:
        feed["authors"] = [{"name": global_post_meta["defaults"]["author"]}]

    # List the most recent 5 posts available
    feed["items"] = []
    for post in tuple(all_posts.values())[:5]:
        item = {
            "id": post.meta["slug"],
            "url": f"{site_meta['domain']}{post.meta['url']}",
            "title": post.meta["title"],
            "subtitle": post.meta.get("subtitle", global_post_meta["defaults"]["subtitle"]),
            "date_published": datetime.combine(post.meta["date"], time.min)
            .replace(tzinfo=UTC)
            .isoformat(),
            "content_html": post.content,
        }
        feed["items"].append(item)

    return json.dumps(feed)
