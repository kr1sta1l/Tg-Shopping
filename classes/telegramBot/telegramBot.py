from classes.localizer import Localizer
from classes.constants import botConstants
from classes.databases.userDatabase import UserDatabase
from classes.databases.queueDatabase import QueueDatabase
from classes.parsers.helperClasses.good import Good
from classes.telegramBot.user import User
from classes.query import Query

import telebot
from telebot import types


class TelegramBot:
    def __init__(self, token, path_to_db, localizer: Localizer, users_database: UserDatabase,
                 queues_database: QueueDatabase):
        self.bot = telebot.TeleBot(token)
        self.path_to_db = path_to_db
        self.localizer: Localizer = localizer
        self.users_database: UserDatabase = users_database
        self.queues_database: QueueDatabase = queues_database

        @self.bot.message_handler(commands=['start'])
        def start_message(message) -> None:
            """
            Handles /start command
            :param message: message to handle
            :return: None
            """
            if self.is_personal_chat(message):
                self.start_message_process(message)

        @self.bot.message_handler(commands=['help'])
        def help_message_handler(message) -> None:
            """
            Handles /help command
            :param message: message to handle
            :return: None
            """
            if self.is_personal_chat(message):
                self.help_message_process(message)

        @self.bot.message_handler(commands=['switch_language'])
        def switch_language_handler(message) -> None:
            """
            Handles switch language button
            :param message: message to handle
            :return: None
            """
            if not self.is_personal_chat(message):
                return
            user = self.users_database.get_user(message.from_user.id)
            if user is None:
                self.send_command_message(message, 'error_message')
                return
            self.send_switch_language_message(message, user)

        @self.bot.message_handler(commands=['admin_menu'])
        def admin_menu_handler(message) -> None:
            """
            Handles admin menu button
            :param message: message to handle
            :return: None
            """
            if self.is_personal_chat(message):
                user = self.users_database.get_user(message.from_user.id)
                if user is None:
                    self.send_command_message(message, 'error_message')
                    return
                if not user.is_admin:
                    return
                self.bot.send_message(message.chat.id,
                                      self.localizer.get_localized_text(user.language, "admin_menu"),
                                      reply_markup=TelegramBot.get_admin_keyboard(user.language), parse_mode='Markdown')

        @self.bot.message_handler(content_types=['text'])
        def text_message_handler(message) -> None:
            """
            Handles text messages
            :param message: message to handle
            :return: None
            """
            print(f"message: {message}")
            if self.is_personal_chat(message):
                self.text_message_process(message)

        @self.bot.callback_query_handler(func=lambda call: call.data in botConstants.AVAILABLE_LANGUAGES)
        def language_callback_handler(call) -> None:
            """
            Handles language callback
            :param call: callback query to handle
            :return: None
            """
            user = self.users_database.get_user(call.from_user.id)
            if user is None:
                self.send_command_message(call.message, 'error_message')
                return
            user.language = call.data
            self.users_database.add_user(user)
            try:
                self.bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            self.send_command_message(call.message, 'language_changed_message',
                                      message_format_values={
                                          "language": botConstants.LANGUAGES_CHARACTERISTICS[user.language][
                                              "name"]},
                                      parse_mode='Markdown', user_id=call.from_user.id,
                                      reply_keyboard_id="start_message_reply_commands")

        @self.bot.callback_query_handler(func=lambda call: call.data.split("_", 1)[0] == "admin")
        def admin_menu_callback_handler(call) -> None:
            """
            Handles admin menu callback
            :param call: callback query to handle
            :return: None
            """
            admin_command = call.data.split("_", 1)[1]
            user = self.users_database.get_user(call.from_user.id)
            if user is None:
                self.send_command_message(call.message, 'error_message')
                return
            if not user.is_admin:
                return
            # self.send_text_message(call.message.chat.id, parse_mode='Markdown')

    def start_message_process(self, message):
        """
        Process /start command
        :param message: message to handle
        :return: id of sent message or None if message wasn't sent
        """
        user = self.users_database.get_user(message.from_user.id)
        # reply_keyboard = TelegramBot.get_reply_keyboard(user.language)
        if user is None:
            user_language = TelegramBot.get_user_language(message)
            user = User(message.from_user.id, "common", user_language, False)
            if user.tg_id in botConstants.ADMINS_ID:
                user.is_admin = True
                user.status = "prime"
            self.users_database.add_user(user)

        reply_message_id = self.send_command_message(
            message, 'greeting_message_with_name', message_format_values={'user_name': message.from_user.first_name},
            parse_mode='Markdown', reply_keyboard_id="start_message_reply_commands")

        if reply_message_id is None:
            return self.send_command_message(message, 'greeting_message', parse_mode='Markdown',
                                             reply_keyboard_id="start_message_reply_commands")
        return reply_message_id

    def send_switch_language_message(self, message, user: User):
        self.bot.send_message(message.chat.id,
                              self.localizer.get_localized_text(user.language, "available_languages"),
                              reply_markup=TelegramBot.get_language_keyboard(), parse_mode='Markdown')

    def help_message_process(self, message):
        """
        Process /help command
        :param message: message to handle
        :return: id of sent message or None if message wasn't sent
        """
        user = self.users_database.get_user(message.from_user.id)
        find_command = self.localizer.get_localized_text(user.language, "find_commands")[0].title()
        without_command = self.localizer.get_localized_text(user.language, "without_commands")[0].upper()
        return self.send_command_message(message, 'help_message',
                                         message_format_values={
                                             "find_command": find_command,
                                             "without_command": without_command},
                                         parse_mode='Markdown')

    def send_command_message(self, message, reply_key, message_format_values: dict[str, str] = None,
                             parse_mode: str = None,
                             user_id: int = None,
                             reply_keyboard_id=None):
        """
        Sends command messages
        :param message: message to send
        :param reply_key: key of message to send
        :param message_format_values:
        :param parse_mode: parse mode of message
        :param user_id: id of user to send message to. If None, message will be sent to message.from_user.id
        :param reply_keyboard_id: id of reply keyboard to send
        :return: id of sent message or None if message wasn't sent
        """
        if user_id is None:
            user_id = message.from_user.id
        user = self.users_database.get_user(user_id)
        if user is None:
            language = TelegramBot.get_user_language(message)
        else:
            language = user.language

        reply_keyboard = None
        if reply_keyboard_id is not None:
            reply_keyboard = TelegramBot.get_reply_keyboard(language, reply_keyboard_id)

        sent_message_id = self.send_text_message(message.chat.id,
                                                 self.localizer.get_localized_text(language, reply_key),
                                                 message_format_values=message_format_values, parse_mode=parse_mode,
                                                 reply_keyboard=reply_keyboard)
        if sent_message_id is None:
            return self.send_text_message(message.chat.id, self.localizer.get_localized_text(language, reply_key),
                                          parse_mode=parse_mode, reply_keyboard=reply_keyboard)
        return sent_message_id

    def send_text_message(self, chat_id, message, message_format_values: dict[str, str] = None, reply_keyboard=None,
                          parse_mode=None, reply_to_message_id=None):
        """
        Sends text message
        :param chat_id: chat id to send message to
        :param message: message to send
        :param message_format_values: format of message
        :param reply_keyboard: reply keyboard to send
        :param parse_mode: parse mode of message
        :param reply_to_message_id: id of message to reply to
        :return: id of sent message or None if message wasn't sent
        """
        if message_format_values is not None:
            message = message.format(**message_format_values)
        try:
            return self.bot.send_message(chat_id, message, parse_mode=parse_mode, reply_markup=reply_keyboard,
                                         reply_to_message_id=reply_to_message_id)
        except Exception as e:
            print(e)
            return None

    def send_reply_text_message(self, message_reply_to, message, message_format_values: dict[str, str] = None,
                                reply_keyboard=None, parse_mode=None):
        """
        Sends text message
        :param message_reply_to: message to reply to
        :param chat_id: chat id to send message to
        :param message: message to send
        :param message_format_values: format of message
        :param reply_keyboard: reply keyboard to send
        :param parse_mode: parse mode of message
        :return: id of sent message or None if message wasn't sent
        """
        if message_format_values is not None:
            message = message.format(**message_format_values)
        try:
            return self.bot.reply_to(message_reply_to, message, parse_mode=parse_mode, reply_markup=reply_keyboard)
        except Exception:
            return None

    def text_message_process(self, message):
        text = message.text
        split_text = text.split(" ", 1)
        split_text[0] = split_text[0].lower()

        user = self.users_database.get_user(message.from_user.id)
        if split_text[0] in self.localizer.get_localized_text(user.language, "find_commands") and len(split_text) > 1:
            split_text = split_text[1].lower().split(self.localizer.get_localized_text(user.language, "without_commands")[0])
            request = split_text[0]
            ban_words_list = None
            if len(split_text) > 1:
                ban_words_list = split_text[1]
            query = Query(user, request, message.id, ban_words_list)
            self.queues_database.add_to_queue(query)
            return self.send_text_message(message.chat.id,
                                          self.localizer.get_localized_text(user.language,
                                                                            "user_added_to_queue_message"),
                                          parse_mode='Markdown', reply_to_message_id=message.message_id)
        else:
            return self.process_text_commands(message, user)

    def process_text_commands(self, message, user: User):
        flag = True
        text = message.text
        reply_commands_list: dict = self.localizer.get_localized_dict(user.language, "start_message_reply_commands")
        for key in reply_commands_list.keys():
            if reply_commands_list[key] == text:
                if key == "good_searching":
                    flag = False
                    self.help_message_process(message)
                elif key == "change_language":
                    flag = False
                    self.send_switch_language_message(message, user)
                elif key == "help":
                    flag = False
                    sent_message = self.localizer.get_localized_text(user.language, "greeting_message")
                    self.send_text_message(user.tg_id, sent_message, parse_mode="Markdown")
        if flag:
            self.help_message_process(message)

    def send_good_list_to_user(self, user_id, goods_list: list[Good], reply_to_message_id: int):
        user = self.users_database.get_user(user_id)
        text = ""
        for good in goods_list:
            text += self.localizer.localize_good_info(user.language, good.get_info()) + "\n\n"
        if len(goods_list) == 0:
            text = self.localizer.get_localized_text(user.language, "cant_find_products_message")
        return self.send_text_message(user_id, text, parse_mode='Markdown', reply_to_message_id=reply_to_message_id)

    def notify_about_start(self, user_id: int, reply_to_message_id: int):
        user = self.users_database.get_user(user_id)
        text = self.localizer.get_localized_text(user.language, "started_processing_the_request_message")
        return self.send_text_message(user_id, text, parse_mode='Markdown', reply_to_message_id=reply_to_message_id)

    def start(self):
        """
        Starts bot
        :return: None
        """
        print('Bot started')
        self.bot.polling()

    @staticmethod
    def is_personal_chat(message) -> bool:
        """
        Checks if message is from personal chat
        :param message: message to check
        :return: True if message is from personal chat, False otherwise
        """
        try:
            return message.chat.id == message.from_user.id
        except Exception:
            return False

    @staticmethod
    def get_user_language(message) -> str:
        """
        Sets user language
        :param message: message to get language from
        :return: language of user
        """
        try:
            language = message.from_user.language_code.strip()
            if language not in botConstants.AVAILABLE_LANGUAGES:
                language = botConstants.DEFAULT_LANGUAGE
        except Exception:
            language = botConstants.DEFAULT_LANGUAGE
        return language

    @staticmethod
    def get_language_keyboard():
        """
        Creates language keyboard
        :return: language keyboard
        """
        keyboard = types.InlineKeyboardMarkup()
        for language in botConstants.AVAILABLE_LANGUAGES:
            language_flag = botConstants.LANGUAGES_CHARACTERISTICS[language]['flag']
            language_name = botConstants.LANGUAGES_CHARACTERISTICS[language]['name']
            keyboard_text = f"{language_flag} {language_name}"
            keyboard.add(types.InlineKeyboardButton(keyboard_text, callback_data=language))
        return keyboard

    @staticmethod
    def get_admin_keyboard(admin_language: str):
        """
        Creates admin keyboard
        :return: admin keyboard
        """
        keyboard = types.InlineKeyboardMarkup()
        for command in botConstants.ADMIN_COMMANDS[admin_language]:
            command_value = botConstants.ADMIN_COMMANDS[admin_language][command]
            keyboard.add(types.InlineKeyboardButton(command_value, callback_data="admin_" + command))
        return keyboard

    @staticmethod
    def get_reply_keyboard(language: str, key: str = None):
        """
        Creates reply keyboard
        :param language: language of keyboard
        :param key: key of keyboard
        :return: reply keyboard
        """
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for command in botConstants.REPLY_COMMANDS[language][key]:
            keyboard.add(types.KeyboardButton(botConstants.REPLY_COMMANDS[language][key][command]))
        return keyboard
