from time import time

from src import models
from src.app import config, create_app
from src.core import helpers


def main() -> None:
    # Get the current time for a bit of info about runtime
    start_time = time()

    # Create an instance of the generator app
    app = create_app()

    all_posts = {}

    # Find all markdown files in the posts directory
    for file in config.get("directories")["posts"].glob("*.md"):
        all_posts[file.name] = models.Post(file)

    # Create all of the directories that we need for dist
    # helpers.make_dist()

    # Provide a basic "how long did it run" message
    print(f"Total generation time: {helpers.duration(time() - start_time)}")


if __name__ == "__main__":
    main()
