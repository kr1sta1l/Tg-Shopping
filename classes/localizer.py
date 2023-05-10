import json


class Localizer:
    def __init__(self, path_to_languages_file, languages: list[str]):
        """
        Class that contains all messages for bot in different languages
        :param path_to_languages_file: path to folder with languages
        :param languages: list of languages
        """
        self.__path_to_languages_file = path_to_languages_file
        self.__languages = languages
        self.__messages = dict()

        for language in languages:
            self.__messages[language] = self.load_language(language)

    def load_language(self, language: str):
        """
        Loads language from file
        :param language: language to load
        :return: dict with messages
        """
        with open(f"{self.__path_to_languages_file}/{language}/bot-messages.json") as file:
            return json.load(file)

    def get_localized_text(self, language: str, message_name: str) -> str:
        """
        Gets localized text
        :param language: language to get text
        :param message_name: message name to get
        :return: localized text
        """
        return self.__messages[language][message_name]

    def get_localized_dict(self, language: str, message_name: str) -> dict[str, str]:
        """
        Gets localized dict
        :param language: language to get dict
        :param message_name: message name to get
        :return: localized dict
        """
        return self.__messages[language][message_name]

    def get_languages(self):
        """
        Gets all languages
        :return: all languages
        """
        return self.__languages

    def localize_good_info(self, language: str, good_info_text: str):
        """
        Localizes good info
        :param language: language to localize
        :param good_info_text: info about good
        :return: localized good info
        """
        convert_dict: dict = self.__messages[language]["good_info_message"]
        for key in convert_dict.keys():
            good_info_text = good_info_text.replace(key, convert_dict[key])
        return good_info_text

