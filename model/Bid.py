from datetime import datetime
from sirope import OID


class Bid:

    def __init__(self, product_oid: OID, amount: float, date: datetime, email_owner: str):
        self.__product_oid = product_oid
        self.__amount = amount
        self.__date = date
        self.__email_owner = email_owner
        ...

    @property
    def product_oid(self) -> OID:
        return self.__product_oid

    @property
    def amount(self) -> float:
        return self.__amount

    @property
    def date(self) -> datetime:
        return self.__date

    @property
    def email_owner(self) -> str:
        return self.__email_owner

    def __str__(self) -> str:
        return f"Product id: {self.__product_oid} - {self.__amount}€ - {self.date} - owner: {self.__email_owner}"

    def get_safe_id(self, srp) -> str:
        return srp.safe_from_oid(self.__oid__)
    ...
