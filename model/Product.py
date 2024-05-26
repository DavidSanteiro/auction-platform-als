from datetime import datetime
import uuid


class Product:
    def __init__(self, title, description, initial_price, auction_open_date, auction_close_date,
                 media_file_names, email_owner):
        self.__title = title
        self.__description = description
        self.__initial_price = initial_price
        self.__price = self.__initial_price
        self.__auction_open_date = auction_open_date
        self.__auction_close_date = auction_close_date
        self.__email_owner = email_owner
        self.__media_file_names = media_file_names
        self.__id = str(uuid.uuid4())
        self.__bids_oid = []
        ...

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, name):
        self.__title = name

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description

    @property
    def initial_price(self):
        return self.__price

    @initial_price.setter
    def initial_price(self, initial_price):
        self.__price = initial_price

    @property
    def auction_open_date(self):
        return self.__auction_open_date

    @auction_open_date.setter
    def auction_open_date(self, auction_open_date):
        self.__auction_open_date = auction_open_date

    @property
    def auction_close_date(self):
        return self.__auction_close_date

    @auction_close_date.setter
    def auction_close_date(self, auction_close_date):
        self.__auction_close_date = auction_close_date

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        self.__price = price

    @property
    def email_owner(self):
        return self.__email_owner

    @property
    def id(self):
        return self.__id

    @property
    def media_file_names(self):
        return self.__media_file_names.copy()

    def add_media_file_name(self, file_name):
        self.__media_file_names.append(file_name)

    def remove_media_file_name(self, file_name):
        self.__media_file_names.remove(file_name)

    @property
    def status(self) -> str:
        current_date = datetime.now()
        if self.__auction_open_date <= current_date <= self.__auction_close_date:
            return "open"
        elif self.__auction_open_date > current_date:
            return "programmed"
        else:
            return "closed"

    @property
    def bids_oid(self):
        return self.__bids_oid.copy()

    def add_bid_oid(self, bid_oid):
        self.__bids_oid.append(bid_oid)

    def get_safe_id(self, srp):
        return srp.safe_from_oid(self.__oid__)
    ...
