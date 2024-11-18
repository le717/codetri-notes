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
            config.get("directories")["output"]
            / config.get("post")["output_dir"]
            / f"{post_model.meta['slug']}.html",
            post_model.to_html(ctx),
        )

    # Provide a basic "how long did it run" message
    print(f"Total generation time: {helpers.duration(time() - start_time)}")


if __name__ == "__main__":
    main()
