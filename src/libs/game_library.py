import json
import os
from loguru import logger
from prompt_toolkit import enums

env = os.getenv


def open_library(library_path) -> dict:
    try:
        # return open(library, encoding="utf8")
        with open(library_path, encoding="utf8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        logger.error("Library not found: %s\nError: %s" % (library_path, str(e)))
    except TypeError as e:
        logger.error("Check your .env files has been updated. Error: " + str(e))
        exit(1)


library_dict = {}


def update_library(library_json: dict, root_json: str):
    logger.info("Updating library dictionary with %s" % root_json)
    try:
        for i in library_json[root_json]:
            if "gog" in str(library_json):
                appname = i["app_name"] + "_gog"
            if "legendary" in str(library_json):
                appname = i["app_name"] + "_legendary"
            if "nile" in str(library_json):
                appname = i["app_name"] + "_nile"

            try:
                if i["app_name"] != "gog-redist_gog":
                    library_dict.update({i["title"]: appname})
            except KeyError:
                continue

    except (KeyError, AttributeError) as e:
        logger.error(str(e) + ". Game library likely not found.")


libraries = ["GOG_LIBRARY", "AMAZON_LIBRARY", "EPIC_LIBRARY"]
for library in libraries:
    if library in os.environ and os.environ[library] != "":
        library_path = os.path.join(env("PATHO"), env(library))
        library_json = open_library(library_path)
        update_library(library_json, root_json="games" if library == "GOG_LIBRARY" else "library")


