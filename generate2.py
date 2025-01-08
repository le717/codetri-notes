from time import time

from src import models
from src.app import config, create_app
from src.core import helpers


def main() -> None:
    # Get the current time for a bit of info about runtime
    start_time = time()

    # Create an instance of the generator app
    create_app()

    # Create all of the directories that we need for dist
    helpers.make_dist()

    # Find all markdown files in the posts directory
    all_posts: dict[str, models.Post] = {
        file.name: models.Post(file) for file in config.get("directories")["posts"].glob("*.md")
    }

    # Sort all of the posts, with the newest on top
    all_posts = {
        k: v for k, v in sorted(all_posts.items(), key=lambda x: x[1].meta["date"], reverse=True)
    }

    # Create a mapping between each post and it's final url
    post_url_mapping = {
        post_model.file.name: post_model.meta["url"] for post_model in all_posts.values()
    }

    # Render, generate, and save to disk each individual post
    for post_model in all_posts.values():
        # We provide the raw file name -> url mapping to allow internal blog links to be generated
        post_model.from_markdown(post_model.meta | {"all_urls": post_url_mapping})

        # All post data is namespaced to make the source of the data clear at all times
        ctx = {"post": {"meta": post_model.meta, "content": post_model.content}}

        # Construct the proper output path for this post and save it to disk
        post_model.to_file(
            config.get("directories")["output_dir"]
            / config.get("post")["output_dir"]
            / f"{post_model.meta['slug']}.html",
            post_model.to_html(ctx),
        )

    # Create the post index, listing all the posts, saving it in the proper place
    # depending on the author's decision to have a distinct home page
    post_index = models.PostIndex(config.get("directories")["theme"])
    post_index_output_dir = (
        config.get("directories")["output_dir"] / config.get("post")["output_dir"]
        if "home_template" in config.get("site")["pages"]
        else config.get("directories")["output_dir"]
    )

    post_index.to_file(
        post_index_output_dir / "index.html", post_index.to_html({"posts": all_posts.values()})
    )

    # If a distinct site homepage has been defined, generate it too
    if "home_template" in config.get("site")["pages"]:
        site_index = models.Page(
            file=config.get("directories")["theme"], template_key="home_template"
        )
        site_index.to_file(
            config.get("directories")["output_dir"] / "index.html", site_index.to_html()
        )

    # Generate all defined pages
    for k, v in config.get("site")["pages"].items():
        # But skip the home page because that's special
        if k == "home_template":
            continue

        site_page = models.Page(config.get("directories")["theme"], template_key=k)
        site_page.to_file(
            config.get("directories")["output_dir"] / v.replace(".jinja2", ".html"),
            site_page.to_html(),
        )

    # If we want to generate feeds, do so
    if config.get("feed"):
        from src.core.feed import generate_json_feed

        (config.get("directories")["output_dir"] / "feed.json").write_text(
            generate_json_feed(all_posts)
        )

    # Provide a basic "how long did it run" message
    print(f"Total generation time: {helpers.duration(time() - start_time)}")


if __name__ == "__main__":
    main()
