class Good:
    def __init__(self, brand: str = None, name: str = None, price: float = None, prev_price: int = None, rating: float = None,
                 delivery_date: str = None, feedback_amount: int = None, url: str = None, photo_url: str = None,
                 shop: str = None):
        """
        Good class
        :param brand: brand of good
        :param name: name of good
        :param price: price of good
        :param prev_price: previous price of good
        :param rating: rating of good
        :param delivery_date: delivery date of good
        :param feedback_amount: amount of feedbacks of good
        :param url: url of good
        :param photo_url: photo url of good
        :param shop: shop name of good
        """
        self.brand: str = brand
        self.name: str = name
        self.price: float = price
        self.prev_price: int = prev_price
        self.rating: float = rating
        self.rate_counter: int = feedback_amount
        self.delivery_date: str = delivery_date
        self.url: str = url
        self.photo_url: str = photo_url
        self.sale: int = 0
        self.shop = shop

        if self.price is not None and self.prev_price is not None:
            self.sale = int(round((self.prev_price - self.price) / self.prev_price, 2) * 100)

        if self.name is None or self.price is None or self.url is None:
            raise Exception("Invalid good data")

    def get_info(self) -> str:
        """
        Gets info about good
        :return: info about good
        """
        text = ""
        if self.shop is not None:
            text += f"🏬 *shop_name_title:* {self.shop}\n"

        text += f"🏷 *good_name_title:* {self.brand + ' | ' if self.brand is not None else ''}{self.name}\n" \
                f"💵 *price_title:* {int(self.price) if int(self.price) == self.price else self.price} ₽"
        if self.sale != 0:
            text += f" (sale_title {self.sale}%)"
        text += "\n"

        if self.rating is not None:
            text += f"⭐ *rate_title:* {self.rating}"
            if self.rate_counter is not None:
                rate_title = "multiple_reviews_title"
                if self.rate_counter == 1:
                    rate_title = "one_review_title"
                text += f" ({self.rate_counter} {rate_title})"
            text += "\n"

        text += f"🛍 *good_link_title:* [click_title]({self.url})"

        return text
