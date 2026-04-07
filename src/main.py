"""
Main entrypoint

Runs envcheck then sets categories
"""

from loguru import logger
from dotenv import load_dotenv
from time import time

load_dotenv()


def timer(func):
    # This function shows the execution time of
    # the function object passed
    def wrap_func(*args, **kwargs):
        logger.info(f"Running {func.__name__!r}...")
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        logger.info(f"Function {func.__name__!r} executed in {(t2 - t1):.4f}s")
        return result

    return wrap_func


@timer
def env_check():
    # uses prompt_toolkit for interactive .env config and validation
    from libs.env_check_prompt import env_check

    env_check()


@timer
def heroic_categories():
    from libs.heroic_categories import heroic_categories

    heroic_categories()


@timer
def categorize_game_list():
    from libs.get_categories_for_game import categorize_game_list

    categorize_game_list()


def main():
    env_check()  # Check .env file and prompt if missing/invalid
    heroic_categories()  # Create categories in heroic
    categorize_game_list()  # Add categories to games in heroic based on IGDB genres
    logger.info("Done. Restart Heroic")


if __name__ == "__main__":
    main()
