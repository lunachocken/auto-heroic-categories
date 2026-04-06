"""Prompt based version of env_check"""

import os
from loguru import logger
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import checkboxlist_dialog, input_dialog
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter
from prompt_toolkit.contrib.completers.system import SystemCompleter
import dotenv

dotenv.load_dotenv()

basic_env_keys = ["CLIENT_ID", "CLIENT_SECRET", "PATHO", "HEROIC_CONFIG"]
optional_env_keys = {
    "epicgames": "EPIC_LIBRARY",
    "gog": "GOG_LIBRARY",
    "amazon": "AMAZON_LIBRARY",
}


def check_minimum_env():
    """Check if min env key vars are set"""
    valid = True
    for key in basic_env_keys:
        if key not in os.environ or os.environ[key] == "":
            logger.error(f"Missing env key: {key}")
            valid = False
    return valid


def basic_valid(text):
    """Validator for basic env keys
    Does the following:

    - Check empty input

    - PATHO and HEROIC_CONFIG:
        - Check if absolute path
        - Check if path exists
        - HEROIC_CONFIG must be a .json file
        - PATHO must be a directory
    """

    class BasicValidator(Validator):
        def validate(self, document):
            if document.text.strip() == "":
                raise ValidationError(
                    message="This field cannot be empty.",
                    cursor_position=len(document.text),
                )
            # path based validation for PATHO and HEROIC_CONFIG
            if text in ["PATHO", "HEROIC_CONFIG", "optional"]:
                # Optional needs to test combined
                text_data=os.path.join(os.environ["PATHO"], document.text.strip()) if text == "optional" else document.text.strip()
                if not os.path.isabs(text_data):
                    raise ValidationError(
                        message="Please enter an absolute path.",
                        cursor_position=len(document.text),
                    )
                if not os.path.exists(text_data):
                    raise ValidationError(
                        message="Path does not exist.",
                        cursor_position=len(document.text),
                    )
                if text in ["HEROIC_CONFIG", "optional"]:
                    if not document.text.strip().endswith(".json"):
                        raise ValidationError(
                            message="HEROIC_CONFIG must be a .json file.",
                            cursor_position=len(document.text),
                        )
            if text == "PATHO" and not os.path.isdir(document.text.strip()):
                raise ValidationError(
                message="PATHO must be a valid directory.",
                    cursor_position=len(document.text),
                )

    return BasicValidator()

def find_heroic_config():
    """Find heroic config file in common locations"""
    possible_locations = [
        os.path.expanduser("~/.config/heroic/config.json"),
        os.path.expanduser("~/AppData/Roaming/heroic/config.json"),
        os.path.expanduser("~/Library/Application Support/heroic/config.json"),
    ]
    for location in possible_locations:
        if os.path.exists(location):
            return location
    return None

def find_patho():
    """Find PATHO='/home/yourUser/.var/app/com.heroicgameslauncher.hgl/config/heroic/store_cache/'
    in common locations"""
    possible_locations = [
        os.path.expanduser("~/.var/app/com.heroicgameslauncher.hgl/config/heroic/store_cache/"),
        os.path.expanduser("~/.config/heroic/store_cache/"),
        os.path.expanduser("~/AppData/Roaming/heroic/store_cache/"),
        os.path.expanduser("~/Library/Application Support/heroic/store_cache/"),
    ]
    for location in possible_locations:
        if os.path.exists(location):
            return location
    return None

def compile_options(key):
    """Compile options for prompt completer based on key"""
    if key == "HEROIC_CONFIG":
        found_config = find_heroic_config()
        if found_config:
            return [found_config]
    elif key == "PATHO":
        found_patho = find_patho()
        if found_patho:
            return [found_patho]
    elif key in optional_env_keys.values():
        # For optional env keys, suggest the PATHO as base path if it exists
        patho = os.environ.get("PATHO", "")
        if patho and os.path.exists(patho):
            return ["gog_library.json", "legendary_library.json", "amazon_library.json"]
    return []

def prompt(env_key, part="1/3", optional=False):
    example_env = dotenv.dotenv_values("env_example") or {}
    options = compile_options(env_key)
    completer = WordCompleter(options, ignore_case=True)

    # Session seems to work better than dialog as autocomplete is weird?
    session = PromptSession()

    print(f"\n--- Environment Variable Setup ({part}) ---")
    print(f"Example: {example_env.get(env_key, '')}")

    try:
        # complete_while_typing=True makes suggestions appear instantly
        # vi_mode=False ensures standard keybindings
        result = session.prompt(
            f"Input value for {env_key}: ",
            completer=completer,
            complete_while_typing=True, 
            validator=basic_valid(env_key if not optional else "optional"),
        )
        if result is "" or len(result) < 5: # Could be cancelled
            raise KeyboardInterrupt
        return result
    except KeyboardInterrupt:
        return None


def prompt_env():
    """Prompt user to update env variables if missing or if they want to update them"""

    for key in basic_env_keys:
        if os.environ.get(key, "") == "":
            val = prompt(key)
            if val is not None and val != "":
                os.environ[key] = val

    # Save basic env keys to .env file
    with open(".env", "w") as f:
        for key in basic_env_keys:
            f.write(f"{key}={os.environ[key]}\n")

    # if any optional env keys are set, skip the prompt
    if any(os.environ.get(opt_key, "") != "" for opt_key in optional_env_keys.values()):
        return

    optional = checkboxlist_dialog(
        title="Game Store Support (2/3)",
        text="Which game stores do you want to utilise? (Enter to skip)",
        values=[("epicgames", "Epic Games"), ("gog", "GOG"), ("amazon", "Amazon")],
        # validate path exists but not required
    ).run()
    if optional is not None and len(optional) > 0:
        for store in optional:
            opt_key = optional_env_keys[store]
            val = prompt(opt_key, part="3/3", optional=True,)
            if val is not None and val != "":
                os.environ[opt_key] = val
    else:
        logger.info("User cancelled optional env setup. Exiting")
        exit(0)
    # Save optional env keys to .env file
    with open(".env", "a") as f:
        for opt_key in optional_env_keys.values():
            if os.environ.get(opt_key, "") != "":
                f.write(f"{opt_key}={os.environ[opt_key]}\n")

    # Validate minimum env keys
    if not check_minimum_env():
        for key in basic_env_keys:
            if key not in os.environ or os.environ[key] == "":
                logger.error(f"Missing env key: {key}. Please update your .env file.")


def env_check():
    import os

    if os.path.exists(".env"):
        logger.info(".env file found. Checking env keys")
        # check for at least one optional
        if not any(
            os.environ.get(opt_key, "") != "" for opt_key in optional_env_keys.values()
        ):
            prompt_env()
        if not check_minimum_env():
            logger.error("Missing env keys, update .env")
            return
        else:
            logger.info("Env valid")
    else:
        # Env setup
        logger.warning(".env file not found. Starting environment variable setup.")
        prompt_env()


if __name__ == "__main__":
    env_check()
