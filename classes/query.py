from classes.telegramBot.user import User


class Query:
    def __init__(self, user: User, query: str, message_id: int, ban_words_list: list[str] = None):
        """
        Class that contains all info about user request
        :param user: object of User class
        :param query: query to search
        :param message_id: message id to edit
        :param ban_words_list: list of banned words
        """
        self.user_id = user.tg_id
        self.message_id = message_id
        self.user_status = user.status
        self.query = query
        self.ban_words_list = ban_words_list
