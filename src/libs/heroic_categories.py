import json
import libs.get_categories as get_categories
import os

HEROIC_CONFIG = os.getenv("HEROIC_CONFIG")


def heroic_categories():
    custom_categories = open(HEROIC_CONFIG)
    data = json.load(custom_categories)

    # Create empty categories if they don't exist in the heroic config
    if "games" not in data:
        data["games"] = {"customCategories": {}}
    elif "customCategories" not in data["games"]:
        data["games"]["customCategories"] = {}

    set_data = set(data["games"]["customCategories"])

    for i in list(get_categories.category_dict().values()):
        if i not in set_data:
            data["games"]["customCategories"].update({i: []})

    list_data = list(set_data)

    with open(HEROIC_CONFIG, "w") as json_file:
        json.dump(data, json_file, indent=4, separators=(",", ": "))

    custom_categories.close()
