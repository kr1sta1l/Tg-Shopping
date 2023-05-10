import time
import random

from classes.parsers.parser import *
from classes.constants.globalConstants import MAX_RELOAD_ATTEMPTS
from classes.parsers.helperClasses.good import Good


class DNSParser(Parser):
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
        # Prevent loading to increase processing speed
        if self.reload_page_counter > MAX_RELOAD_ATTEMPTS:
            return
        self.init_driver()
        self.driver.get(DNSParser.convert_good_name_to_url(good_name))
        self.close_old_browser_notify()
        try:
            self.__get_goods(needed_good_name=good_name, result_list=result_list, banned_words=banned_words)
        except Exception as e:
            self.reload_page_counter += 1
            # Reload the page to bypass the lock
            self.parse(good_name=good_name, result_list=result_list, banned_words=banned_words)
            try:
                self.driver.close()
                self.reload_page_counter = 0
            except Exception:
                pass
            return
        self.reload_page_counter = 0
        self.driver.close()

    def __get_goods(self, needed_good_name: str, result_list: list[Good], banned_words: list[str] = None):
        """
        Get all goods from page
        :param needed_good_name: needed good name
        :param result_list: list to add goods
        :param banned_words: list of banned words
        :return: None
        """
        goods_set = set()

        good_card_list_web_element = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((
            By.CLASS_NAME, "catalog-products.view-simple")))
        good_card_list_web_element = good_card_list_web_element[-1]

        prev_last_good = None

        # Collecting all goods from page
        for _ in range(3):
            # Get all available goods
            good_card_list = good_card_list_web_element.find_elements(By.CLASS_NAME, "catalog-product.ui-button-widget")
            for good in good_card_list:
                goods_set.add(good)

            # Scroll to last good to load new goods until last good will be the same
            #                                       (it means that there are no more goods)
            if prev_last_good == good_card_list[-1]:
                break
            self.driver.execute_script("arguments[0].scrollIntoView();", good_card_list[-1])
            time.sleep(random.randint(4, 8) / 10)  # To avoid blocking by dns
            # If there are not enough product cards
            try:
                self.driver.find_element(By.CLASS_NAME, "pagination-widget__show-more-btn").click()
            except Exception as e:
                pass
            prev_last_good = good_card_list[-1]

        for i, card in enumerate(list(goods_set)):
            good_name = card.find_element(By.CLASS_NAME, "catalog-product__name.ui-link.ui-link_black").text
            if not Parser.is_needed_good(good_name, needed_good_name, banned_words):
                continue

            try:
                good = DNSParser.create_good(card)
            except Exception as e:
                continue
            result_list.append(good)

    def close_old_browser_notify(self):
        """
        Close old browser notify
        :return: None
        """
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located((
                By.CLASS_NAME, "base-modal__header-close-icon.handler-active")))[-1].click()
        except Exception as e:
            pass

    @staticmethod
    def get_rating(product_card: WebElement):
        """
        Get rating of the good
        :param product_card: product card
        :return: rating and rate counter
        """
        rating_list = product_card.find_element(By.CLASS_NAME, "catalog-product__rating.ui-link.ui-link_black")
        rating = float(rating_list.get_attribute("data-rating"))
        rate_counter = rating_list.text
        rate_counter = rate_counter.replace(" ", "").strip()
        try:
            rate_counter = int(rate_counter)
        except Exception:
            pass
        return rating, rate_counter

    @staticmethod
    def convert_good_name_to_url(good_name: str) -> str:
        """
        Convert good name to url
        :param good_name: name of the good
        :return: url
        """
        return "https://www.dns-shop.ru/search/?q={}&order=price-asc".format(good_name.replace(" ", "+"))

    @staticmethod
    def create_good(good_card: WebElement) -> Good:
        """
        Create good from good card
        :param good_card: good card
        :return: good
        """
        good_brand = None
        good_name = good_card.find_element(By.CLASS_NAME,
                                           "catalog-product__name.ui-link.ui-link_black").text.split("\n")[0]
        good_now_prev_cost = []
        try:
            good_now_prev_cost = good_card.find_element(By.CLASS_NAME,
                                                        "product-buy__price-wrap product-buy__price-wrap_interactive").text.split(
                "₽")
            good_price = int(good_now_prev_cost[0].replace(" ", "").strip())
        except Exception:
            good_price = good_card.find_element(By.CLASS_NAME, "product-buy__price").text
            good_price = int(good_price.split("₽")[0].replace(" ", "").strip())

        good_prev_price = None
        if len(good_now_prev_cost) > 1:
            try:
                good_prev_price = int(good_now_prev_cost[1].replace(" ", "").strip())
            except Exception as e:
                pass

        good_rate, rate_counter = DNSParser.get_rating(good_card)
        # rate_counter = int(good_card.find_element(By.CLASS_NAME, "product-card__count").text)

        good_url = good_card.find_element(By.CLASS_NAME,
                                          "catalog-product__name.ui-link.ui-link_black").get_attribute("href")
        good_image_url = None
        # good_image_url = good_card.find_element(By.CLASS_NAME, "catalog-product__image-link").get_attribute("picture")
        return Good(brand=good_brand, name=good_name, price=good_price, prev_price=good_prev_price, url=good_url,
                    photo_url=good_image_url, rating=good_rate, feedback_amount=rate_counter, shop="DNS")
