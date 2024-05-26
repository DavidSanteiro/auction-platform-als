from datetime import datetime
from sirope import OID


class Product:
    def __init__(self, title: str, description: str, initial_price: float, auction_open_date: datetime,
                 auction_close_date: datetime, media_file_names: [str], email_owner: str):
        self.__title = title
        self.__description = description
        self.__initial_price = initial_price
        self.__price = initial_price
        self.__auction_open_date = auction_open_date
        self.__auction_close_date = auction_close_date
        self.__email_owner = email_owner
        self.__media_file_names = media_file_names
        self.__bids_oid = []
        self.__comments_oid = []
        ...

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, name: str):
        self.__title = name

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, description: str):
        self.__description = description

    @property
    def initial_price(self) -> float:
        return self.__initial_price

    @initial_price.setter
    def initial_price(self, initial_price: float):
        self.__price = round(initial_price, 2)

    @property
    def auction_open_date(self) -> datetime:
        return self.__auction_open_date

    @auction_open_date.setter
    def auction_open_date(self, auction_open_date: datetime):
        self.__auction_open_date = auction_open_date

    @property
    def auction_close_date(self) -> datetime:
        return self.__auction_close_date

    @auction_close_date.setter
    def auction_close_date(self, auction_close_date: datetime):
        self.__auction_close_date = auction_close_date

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, price: float):
        self.__price = price

    @property
    def email_owner(self) -> str:
        return self.__email_owner

    # Media files

    @property
    def media_file_names(self) -> [str]:
        return self.__media_file_names.copy()

    def add_media_file_name(self, file_name: str):
        self.__media_file_names.append(file_name)

    def remove_media_file_name(self, file_name: str):
        self.__media_file_names.remove(file_name)

    # Comments OIDs

    def add_comment_oid(self, comment: OID):
        self.__comments_oid.append(comment)

    def remove_comment_oid(self, comment: OID):
        self.__comments_oid.remove(comment)

    def get_comments_oid(self) -> [OID]:
        return self.__comments_oid.copy()

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
    def bids_oid(self) -> [OID]:
        return self.__bids_oid.copy()

    def add_bid_oid(self, bid_oid: OID):
        self.__bids_oid.append(bid_oid)

    def get_safe_id(self, srp) -> str:
        return srp.safe_from_oid(self.__oid__)
    ...
