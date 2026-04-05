"""
Main entrypoint

Runs envcheck then sets categories
"""
from dotenv import load_dotenv
load_dotenv()

def env_check():
    # uses prompt_toolkit for interactive .env config and validation
    from libs.env_check_prompt import env_check
    env_check()

def heroic_categories():
    from libs.heroic_categories import heroic_categories
    heroic_categories()

def categorize_game_list():
    from libs.get_categories_for_game import categorize_game_list
    categorize_game_list()

def main():
    env_check() # Check .env file and prompt if missing/invalid
    heroic_categories() # Create categories in heroic
    categorize_game_list() # Add categories to games in heroic based on IGDB genres

if __name__ == "__main__":
    main()
