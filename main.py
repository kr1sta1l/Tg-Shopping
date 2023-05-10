from classes.constants import botConstants
from classes.localizer import Localizer
import threading
from classes.telegramBot.telegramBot import TelegramBot
from classes.databases.userDatabase import UserDatabase
from classes.databases.queueDatabase import QueueDatabase
from classes.parsers.parserSupervisor.parserSupervisor import ParserSupervisor

if __name__ == '__main__':
    localizer = Localizer("./resources/languages",
                          botConstants.AVAILABLE_LANGUAGES)
    database = UserDatabase("./resources/databases/users.db")
    queue_database = QueueDatabase("./resources/databases/queue.db")
    bot = TelegramBot(botConstants.TG_BOT_TOKEN, "./database/users.db", localizer, database, queue_database)
    parser_supervisor = ParserSupervisor(queue_database, database, bot)

    threads = [threading.Thread(target=bot.start), threading.Thread(target=parser_supervisor.run)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
