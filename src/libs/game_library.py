import json
from dotenv import load_dotenv
import os

from prompt_toolkit import enums

env = os.getenv
load_dotenv()


def open_library(library):
    try:
        return open(library, encoding="utf8")
    except FileNotFoundError as e:
        print("Some library locations not found: " + str(e))
    except TypeError as e:
        print("Check your .env files has been updated. Error: " + str(e))
        exit(1)


library_dict = {}


def update_library(library, root_json: str):
    try:
        data = json.load(library)
        for i in data[root_json]:
            if "gog" in str(library):
                appname = i["app_name"] + "_gog"
            if "legendary" in str(library):
                appname = i["app_name"] + "_legendary"
            if "nile" in str(library):
                appname = i["app_name"] + "_nile"

            try:
                if i["app_name"] != "gog-redist_gog":
                    library_dict.update({i["title"]: appname})
            except KeyError:
                continue

        library.close()
    except (KeyError, AttributeError) as e:
        print(str(e) + ". Game library likely not found.")
        library.close()


libs = ["GOG_LIBRARY", "AMAZON_LIBRARY", "EPIC_LIBRARY"]
libraries = {}
for library in libs:
    if library in os.environ and os.environ[library] != "":
        libraries[library + "_PATH"] = os.path.join(env("PATHO"), env(library))
        libraries[library] = open_library(libraries[library + "_PATH"])
        update_library(
            libraries[library], "games" if library == "GOG_LIBRARY" else "library"
        )

# GOG_LIBRARY = os.path.join(env("PATHO"), env("GOG_LIBRARY"))
# AMAZON_LIBRARY = os.path.join(env("PATHO"), env("AMAZON_LIBRARY"))
# EPIC_LIBRARY = os.path.join(env("PATHO"), env("EPIC_LIBRARY"))

# GOG_LIBRARY = open_library(GOG_LIBRARY)
# AMAZON_LIBRARY = open_library(AMAZON_LIBRARY)
# EPIC_LIBRARY = open_library(EPIC_LIBRARY)


# library(GOG_LIBRARY, "games")
# library(AMAZON_LIBRARY, "library")
# library(EPIC_LIBRARY, "library")
