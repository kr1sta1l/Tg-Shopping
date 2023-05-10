from seleniumwire import webdriver
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from classes.parsers.helperClasses.good import Good


class Parser:
    def __init__(self, path_to_driver: str = "./resources/webdriver/chromedriver"):
        path_to_driver = "/home/kr1sta1l/PycharmProjects/Tg Shopping/resources/webdriver/chromedriver"
        self.path_to_driver = path_to_driver
        self.driver = None
        pass

    def init_driver(self):
        """
        Initialize driver
        :return: None
        """
        try:
            self.driver.quit()
        except:
            pass
        useragent = UserAgent()

        ua = useragent.random
        options = Options()
        options.add_argument('log-level=2')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument(f'user-agent={ua}')
        options.page_load_strategy = 'normal'

        # Cheat the site it is not bot)
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--ash-host-window-bounds")
        options.add_argument("--disable-notifications")

        try:
            s = Service(self.path_to_driver)
            self.driver = webdriver.Chrome(service=s, options=options)
            self.driver.maximize_window()
        except Exception as e:
            print("Error while creating driver:", e)  # TODO normal logging
            exit(-1)
        self.driver.delete_all_cookies()

    def parse(self, good_name: str, result_list: list[Good], banned_words: list[str] = None) -> None:
        """
        Parse sites
        :param good_name:
        :param result_list:
        :param banned_words:
        :return:
        """
        self.__get_goods(good_name, result_list, banned_words)

    def __get_goods(self, needed_good_name: str, result_list: list[Good], banned_words: list[str] = None):
        """
        Get goods from site
        :param needed_good_name: name of good to search
        :param result_list: list to add goods
        :param banned_words: words that should not be in good_name
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def convert_good_name_to_url(good_name: str) -> str:
        """
        Convert good name to url
        :param good_name:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def is_needed_good(good_name: str, need_good_name: str, banned_words: list[str] = None) -> bool:
        """
        Simple function to check if good_name contains all words from need_good_name
        :param good_name: where to check
        :param need_good_name: name of good to check
        :param banned_words: words that should not be in good_name
        :return: True if good_name contains all words from need_good_name and does not contain any word from
        banned_words
        """
        need_good_name = need_good_name.lower().split(" ")
        good_name = good_name.lower().split(" ")

        if banned_words is not None:
            for word in banned_words:
                if word in good_name:
                    return False

        if need_good_name is None:
            return False

        for word in need_good_name:
            if word not in good_name:
                return False
        return True

    @staticmethod
    def create_good(good_card: WebElement) -> Good:
        """
        Create Good object from good_card
        :param good_card:
        :return:
        """
        raise NotImplementedError
