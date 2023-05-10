import time
import random

from classes.parsers.parser import *
from classes.parsers.helperClasses.good import Good
from classes.constants.globalConstants import MAX_RELOAD_ATTEMPTS


class WildberriesParser(Parser):
    def __init__(self):
        super().__init__()
        self.reload_counter = 0

    def parse(self, good_name: str, result_list: list[Good], banned_words: list[str] = None) -> None:
        """
        Parse the page with goods
        :param good_name: name of the good
        :param result_list: list to add goods
        :param banned_words: list of banned words
        :return: None
        """
        if self.reload_counter > MAX_RELOAD_ATTEMPTS:
            self.driver.close()
            self.reload_counter = 0
            return
        self.init_driver()
        self.driver.get(WildberriesParser.convert_good_name_to_url(good_name))
        try:
            self.__get_goods(good_name, result_list, banned_words)
        except Exception:
            self.reload_counter += 1
            self.parse(good_name, result_list, banned_words)

        self.driver.close()
        self.reload_counter = 0

    def __get_goods(self, needed_good_name: str, result_list: list[Good], banned_words: list[str] = None) -> None:
        """
        Get all goods from page
        :param needed_good_name: needed good name
        :param result_list: list to add goods
        :param banned_words: list of banned words
        :return: None
        """
        goods_set = set()
        good_card_list_web_element = WebDriverWait(self.driver, 15).until(EC.presence_of_all_elements_located((
            By.CLASS_NAME, "product-card-list")))
        good_card_list_web_element = good_card_list_web_element[-1]

        prev_last_good = None

        # Collecting all goods from page
        while True:
            # Get all available goods
            good_card_list = good_card_list_web_element.find_elements(By.CLASS_NAME, "product-card.j-card-item")
            for good in good_card_list:
                goods_set.add(good)

            # Scroll to last good to load new goods until last good will be the same
            #                                       (it means that there are no more goods)
            if prev_last_good == good_card_list[-1]:
                break
            self.driver.execute_script("arguments[0].scrollIntoView();", good_card_list[-1])
            time.sleep(random.randint(1, 5) / 10)  # To avoid blocking by wildberries
            prev_last_good = good_card_list[-1]

        for i, card in enumerate(list(goods_set)):
            good_name = card.find_element(By.CLASS_NAME, "product-card__brand-wrap").text

            if not Parser.is_needed_good(good_name, needed_good_name):
                continue

            try:
                good = WildberriesParser.create_good(card)
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
        return "https://www.wildberries.ru/catalog/0/search.aspx?page=1&sort=priceup&search={}".format(
            good_name.replace(" ", "+"))

    @staticmethod
    def create_good(good_card: WebElement) -> Good:
        """
        Create good from good card
        :param good_card: good card
        :return: good
        """
        good_brand = good_card.find_element(By.CLASS_NAME, "product-card__brand").text
        good_name = good_card.find_element(By.CLASS_NAME, "product-card__name").text.split("/")[1].strip()
        good_now_prev_cost = good_card.find_element(By.CLASS_NAME, "product-card__price.price").text.split("₽")
        good_price = int(good_now_prev_cost[0].replace(" ", "").strip())
        good_prev_price = None
        if len(good_now_prev_cost) > 1:
            try:
                good_prev_price = int(good_now_prev_cost[1].replace(" ", "").strip())
            except Exception as e:
                pass

        rate_class_name = "product-card__rating.stars-line.star{}"
        good_rate = None
        for i in range(0, 6):
            try:
                good_card.find_element(By.CLASS_NAME, rate_class_name.format(i))
                good_rate = i
                break
            except Exception:
                pass
            if rate_class_name.format(i) in good_card.get_attribute("class"):
                good_rate = i
                break
        rate_counter = int(good_card.find_element(By.CLASS_NAME, "product-card__count").text)

        good_url = good_card.find_element(By.CLASS_NAME,
                                          "product-card__link.j-card-link.j-open-full-product-card").get_attribute(
            "href")
        good_image_url = good_card.find_element(By.CLASS_NAME, "j-thumbnail").get_attribute("src")
        return Good(brand=good_brand, name=good_name, price=good_price, prev_price=good_prev_price, url=good_url,
                    photo_url=good_image_url, rating=good_rate, feedback_amount=rate_counter, shop="Wildberries")
