import time
import random

from classes.parsers.parser import *
from classes.constants.globalConstants import MAX_RELOAD_ATTEMPTS
from classes.parsers.helperClasses.good import Good


class MVideoParser(Parser):
    def __init__(self):
        super().__init__()
        self.reload_page_counter = 0

    def parse(self, good_name: str, result_list: list[Good], banned_words: list[str] = None) -> None:
        """
        Parse the page with goods
        :param good_name: name of the good
        :param result_list: list to add goods
        :param banned_words: list of banned words
        :return: None
        """
        start_url = MVideoParser.convert_good_name_to_url(good_name)
        reload_amount = 0
        while reload_amount < MAX_RELOAD_ATTEMPTS:
            self.init_driver()
            self.driver.get(start_url)
            if not self.is_blocked():
                break

        if reload_amount != MAX_RELOAD_ATTEMPTS:
            self.__get_goods(good_name, result_list, banned_words)
        self.reload_page_counter = 0
        self.driver.close()

    def __get_goods(self, needed_good_name: str, result_list: list[Good], banned_words: list[str] = None) -> None:
        """
        Get all goods from page
        :param needed_good_name: name of the good
        :param result_list: list to add goods
        :param banned_words: list of banned words
        :return: None
        """
        # good_card_list_web_element = self.driver.find_elements(By.CLASS_NAME, "product-card-list")
        good_card_list_web_element = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((
            By.CLASS_NAME, "product-cards-layout.product-cards-layout--grid")))[-1]

        # Get all available goods
        good_lines_list = good_card_list_web_element.find_elements(By.CLASS_NAME,
                                                                   "product-cards-row.ng-star-inserted")

        # Walking through the product lines. One line includes several product cards.
        # The specific device of the product page does not imply convenient (for collection by the parser) storage
        # product cards, so you have to save all the data in the form of a list and then structure it
        # as required
        for i, card in enumerate(good_lines_list):
            good_names_list: list[WebElement] = card.find_elements(By.CLASS_NAME,
                                                                   "product-card__title-line-container.ng-star-inserted")
            good_prices_list: list[WebElement] = card.find_elements(By.CLASS_NAME,
                                                                    "product-card__price-block-container.ng-star-inserted")

            for i in range(len(good_names_list)):
                good_name = good_names_list[i].find_element(By.CLASS_NAME, "product-card__title-line").text
                if not Parser.is_needed_good(good_name, needed_good_name, banned_words):
                    continue
                try:
                    good = MVideoParser.custom_create_good(i, good_prices_list, good_names_list)
                except Exception as e:
                    continue
                result_list.append(good)

    @staticmethod
    def convert_good_name_to_url(good_name: str) -> str:
        """
        Convert good name to url
        :param good_name: name of the good
        :return: url
        """
        return "https://www.mvideo.ru/product-list-page?q={}".format(good_name.replace(" ", "+"))

    @staticmethod
    def custom_create_good(good_index: int, good_prices_list: list[WebElement],
                           good_names_list: list[WebElement]) -> Good:
        """
        Create good from web elements
        :param good_index: index of good
        :param good_prices_list: list of web elements with prices
        :param good_names_list: list of web elements with names
        :return: good
        """
        good_name = good_names_list[good_index].find_element(By.CLASS_NAME, "product-card__title-line").text
        good_prev_now_price = good_prices_list[good_index].find_element(By.CLASS_NAME,
                                                                        "price.price--grid.ng-star-inserted")
        good_prev_price = None
        good_price = int(
            good_prev_now_price.find_element(By.CLASS_NAME, "price__main-value").text.replace(" ", "").replace("₽", ""))
        try:
            good_prev_price = int(
                good_prev_now_price.find_element(By.CLASS_NAME, "price__sale-value.ng-star-inserted").text.
                replace(" ", "").replace("₽", ""))
        except Exception:
            pass

        rating = None
        feedback_amount = None
        try:
            rating_card = good_names_list[good_index].find_element(By.CLASS_NAME, "product-rating.ng-star-inserted")
            rating = rating_card.find_element(By.CLASS_NAME, "value.ng-star-inserted").text
            try:
                rating = float(rating)
            except Exception:
                pass
            feedback_amount = "".join(rating_card.find_element(By.CLASS_NAME,
                                                                   "product-rating__feedback.product-"
                                                                   "rating__feedback--with-link").text.split()[:-1])
            try:
                feedback_amount = int(feedback_amount)
            except Exception:
                pass
        except Exception:
            pass

        url = good_names_list[good_index].find_element(By.CLASS_NAME,
                                                       "product-title__text.product-title--clamp").get_attribute("href")
        return Good(name=good_name, price=good_price, prev_price=good_prev_price, rating=rating,
                    feedback_amount=feedback_amount, url=url, shop="М.Видео")

    def is_blocked(self) -> bool:
        """
        Check if page is blocked
        :return: True if page is blocked, False otherwise
        """
        try:
            if self.driver.find_element(By.CLASS_NAME, "old_br_header"):
                return True
        except Exception:
            pass
        return False
