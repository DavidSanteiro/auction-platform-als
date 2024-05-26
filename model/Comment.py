from datetime import datetime


class Comment:
    def __init__(self, email_author, author_name, text, product_oid):
        self.__email_author = email_author
        self.__author_name = author_name
        self.__date = datetime.now()
        self.__text = text
        self.__product_oid = product_oid

    @property
    def email_author(self):
        return self.__email_author

    @property
    def author_name(self):
        return self.__author_name

    @property
    def date(self):
        return self.__date

    @property
    def text(self):
        return self.__text

    @property
    def product_oid(self):
        return self.__product_oid

    def get_safe_id(self, srp):
        return srp.safe_from_oid(self.__oid__)
    ...
