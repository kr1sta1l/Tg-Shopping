import json

TG_BOT_TOKEN = None
AVAILABLE_LANGUAGES = None
DEFAULT_LANGUAGE = None
ADMINS_ID = None
LANGUAGES_CHARACTERISTICS = None
ADMIN_COMMANDS = None
REPLY_COMMANDS = None
PATH_TO_LOCALIZED_MESSAGES = "./resources/languages/{language}/bot-messages.json"


def load_config() -> dict:
    """
    Loads config from config.json
    :return: config
    """
    with open("./resources/configs/config.json") as file:
        return json.load(file)


def config_to_constants() -> None:
    """
    Loads config from config.json and sets all values as constants
    :return: None
    """
    config = load_config()
    for key in config:
        globals()[key] = config[key]


def load_languages_constants():
    """
    Loads config from config.json
    :return: config
    """
    global AVAILABLE_LANGUAGES
    global ADMIN_COMMANDS
    global REPLY_COMMANDS
    ADMIN_COMMANDS = dict()
    REPLY_COMMANDS = dict()
    if AVAILABLE_LANGUAGES is None:
        config_to_constants()
    for language in AVAILABLE_LANGUAGES:
        REPLY_COMMANDS[language] = dict()
        with open(PATH_TO_LOCALIZED_MESSAGES.format(language=language)) as file:
            json_file = json.load(file)
            ADMIN_COMMANDS[language] = json_file["admin_commands"]
            REPLY_COMMANDS[language]["start_message_reply_commands"] = json_file["start_message_reply_commands"]


if __name__ != '__main__':
    # config_to_constants()
    load_languages_constants()
