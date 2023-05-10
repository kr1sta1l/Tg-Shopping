from classes.parsers.parser import *
from classes.constants.globalConstants import *
from classes.parsers.parsers.wildberriesParser import WildberriesParser
from classes.parsers.parsers.dnsParser import DNSParser
from classes.parsers.parsers.mVideoParser import MVideoParser
from classes.parsers.parsers.globusParser import GlobusParser
from classes.databases.queueDatabase import QueueDatabase
from classes.databases.userDatabase import UserDatabase
from classes.telegramBot.telegramBot import TelegramBot
import threading


class ParserSupervisor:
    def __init__(self, queue_database: QueueDatabase, user_database: UserDatabase, tg_bot: TelegramBot):
        self.parsers = [WildberriesParser(), DNSParser(), MVideoParser(), GlobusParser()]
        # self.parsers = [MVideoParser()]
        self.queue_database = queue_database
        self.user_database = user_database
        self.tg_bot = tg_bot

    def parse(self, good_name: str, banned_words: list[str] = None) -> list[Good]:
        """
        Function that parse all sites
        :param good_name: name of good to search
        :param banned_words: list of banned words
        :return:
        """
        good_name = good_name.strip()
        for i in range(len(banned_words)):
            banned_words[i] = banned_words[i].strip()

        threads = []
        result_list: list[Good] = []
        for parser in self.parsers:
            threads.append(
                threading.Thread(target=parser.parse, args=(good_name, result_list, banned_words)))
        for parser in threads:
            parser.start()

        for thread in threads:
            thread.join()
        return result_list

    def processing_queue(self, user_request: dict[str, str]):
        """
        Function that process user request
        :param user_request: dict with user request
        :return:
        """
        user = self.user_database.get_user(int(user_request["user_id"]))
        if user is None:
            return None
        amount_of_goods = DEFAULT_USER_GOODS_AMOUNT
        if user.status == "prime":
            amount_of_goods = PRIME_USER_GOODS_AMOUNT
        request_result = self.parse(user_request["query"], user_request["banned_words"].split(","))
        if request_result is None:
            return None
        request_result.sort(key=lambda good: good.price)
        request_result = request_result[:amount_of_goods]
        return request_result

    def run(self):
        """
        Main function of parser supervisor
        :return: None
        """
        while True:
            table_name = PRIME_USER_TABLE_NAME
            user_request = self.queue_database.get_user_request(table_name)
            if user_request is None:
                table_name = DEFAULT_USER_TABLE_NAME
                user_request = self.queue_database.get_user_request(table_name)
            if user_request is None:
                continue
            user_request_message_id = user_request["message_id"]
            self.queue_database.delete_user(table_name, user_request["id"])
            self.tg_bot.notify_about_start(user_request["user_id"], user_request_message_id)
            result = self.processing_queue(user_request)
            self.tg_bot.send_good_list_to_user(user_request["user_id"], result, user_request_message_id)
