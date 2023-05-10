import time
import random

from classes.parsers.parser import *
from classes.parsers.helperClasses.good import Good
from classes.constants.globalConstants import MAX_RELOAD_ATTEMPTS


class GlobusParser(Parser):
    def __init__(self):
        super().__init__()
        self.reload_counter = 0

    def parse(self, good_name: str, result_list: list[Good], banned_words: list[str] = None) -> None:
        """
        Parse the page with goods
        :param good_name: name of the good
        :param result_list: list to add goods
        :param banned_words: list of banned words
        :return:
        """
        if self.reload_counter > MAX_RELOAD_ATTEMPTS:
            self.driver.close()
            self.reload_counter = 0
            return

        self.init_driver()
        page_url = GlobusParser.convert_good_name_to_url(good_name)
        self.driver.get(page_url)

        time.sleep(random.randint(2, 3))
        try:
            self.close_choose_region()
            self.__get_goods(good_name, result_list, banned_words)
        except Exception as e:
            self.reload_counter += 1
            self.parse(good_name, result_list, banned_words)
            try:
                self.driver.close()
                self.reload_counter = 0
            except Exception:
                pass
            return

        try:
            page_url = page_url + "&PAGEN_1=2"
            self.driver.get(page_url)
            self.__get_goods(good_name, result_list, banned_words)
        except Exception as e:
            pass

        self.reload_counter = 0
        self.driver.close()

    def __get_goods(self, needed_good_name: str, result_list: list[Good], banned_words: list[str] = None) -> None:
        """
        Get all goods from page
        :param needed_good_name: needed good name
        :param result_list: list to add goods
        :param banned_words: list of banned words
        :return:
        """
        search_page = self.driver.find_element(By.CLASS_NAME, "search-page")
        try:
            goods_web_elements = search_page.find_element(By.TAG_NAME, "ul")
            goods_web_elements = goods_web_elements.find_elements(By.TAG_NAME, "li")
        except Exception:
            return

        good_urls_list = []
        for el in goods_web_elements:
            good_line = el.find_element(By.TAG_NAME, "a")
            good_name = good_line.text
            if Parser.is_needed_good(good_name, needed_good_name, banned_words):
                good_urls_list.append(good_line.get_attribute("href"))

        for i, url in enumerate(good_urls_list):
            self.driver.get(url)
            try:
                good = GlobusParser.create_good(self.driver)
            except Exception as e:
                continue
            result_list.append(good)

    @staticmethod
    def convert_good_name_to_url(good_name: str) -> str:
        """
        Convert good name to url
        :param good_name: good name
        :return: url
        """
        return "https://www.globus.ru/search/?q={}".format(good_name)

    @staticmethod
    def create_good(good_card) -> Good:
        """
        Create good from good card
        :param good_card: good card
        :return: good
        """
        good_url = good_card.current_url
        good_card = WebDriverWait(good_card, 5).until(EC.presence_of_all_elements_located((
            By.CLASS_NAME, "col-xl")))[-1]
        good_name = good_card.find_element(By.CLASS_NAME, "catalog-detail__title").text
        good_rubles = int(good_card.find_element(By.CLASS_NAME, "catalog-detail__item-price-actual-main").text.strip())
        good_kopecks = int(
            good_card.find_element(By.CLASS_NAME, "catalog-detail__item-price-actual-sub").text.strip()) / 100
        good_price = good_rubles + good_kopecks
        good_image_url = good_card.find_element(By.CLASS_NAME,
                                                "js-catalog-detail__header-image-img.catalog-detail__header-image-img").get_attribute(
            "src")
        return Good(url=good_url, name=good_name, price=good_price, photo_url=good_image_url, shop="Globus")

    def close_choose_region(self):
        """
        Close choose region window
        :return: None
        """
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located((
                By.CLASS_NAME, "fancybox-button.fancybox-close-small")))[-1].click()
        except Exception as e:
            pass
