import re
from flask_sqlalchemy import SQLAlchemy
from enum import Enum, EnumMeta, IntEnum

from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from threading import Thread

db = SQLAlchemy()

BEST_BUY = {
    "currentPriceDivAttr": {"class": re.compile("^pricingContainer")},
    "regularPriceDivAttr": {"class": re.compile("^pricingContainer")},
    "titleDivAttr": {"class": "x-product-detail-page"},
    "currentPriceAttr": {"itemprop": "price"},
    "regularPriceAttr": {"class": re.compile(r"^productSaving")},
    "titleAttr": {"class": re.compile("^productName")},
}

AMAZON = {
    "currentPriceDivAttr": {"id": "price"},
    "regularPriceDivAttr": {"id": "price"},
    "titleDivAttr": {"id": "titleSection"},
    "currentPriceAttr": {
        "id": re.compile(r"^priceblock_ourprice$|^priceblock_dealprice$")
    },
    "regularPriceAttr": {"class": "priceBlockStrikePriceString"},
    "titleAttr": {"id": "title"},
}

CANADACOMPUTERS = {
    "currentPriceDivAttr": {"class": "page-product_info"},
    "regularPriceDivAttr": {"class": "page-product_info"},
    "titleDivAttr": {"class": "page-product_info"},
    "availabilityDivAttr": {"class": "page-product_info"},
    "imageDivAttr": {"class": "page-product_info"},
    "currentPriceAttr": {"class": "h2-big"},
    "regularPriceAttr": {"class": "h3 text-nowrap mb-0"},
    "titleAttr": {"class": "h3 mb-0"},
    "availabilityAttr": {"id": "btn-addCart"},
    "imageAttr": {"id": "pi-prod-img-lrg"},
}

PROVINCES = {
    "Alberta": "AB",
    "British Columbia": "BC",
    "Manitoba": "MB",
    "New Brunswick": "NB",
    "Newfoundland and Labrador": "NL",
    "Northwest Territories": "NT",
    "Nova Scotia": "NS",
    "Nunavut": "NU",
    "Ontario": "ON",
    "Prince Edward Island": "PE",
    "Quebec": "QC",
    "Saskatchewan": "SK",
    "Yukon": "YT",
}


def add_to_database(item, func, **kwargs):
    try:
        db.session.add(item)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        db.session.flush()
        if "silent" in kwargs and not kwargs["silent"]:
            raise e
        item = func
    return item


def get_from_database(type, **kwargs):
    if not kwargs:
        return type.query.all()
    if "id" in kwargs:
        return type.query.get(kwargs["id"])
    if "filter" in kwargs:
        return type.query.filter(kwargs["filter"]).all()
    else:
        try:
            funcs = []
            for key, value in kwargs.items():
                if key == "filter":
                    continue
                funcs.append(getattr(type, key) == value)
        except AttributeError as e:
            raise e

        return type.query.filter(and_(*funcs)).all()


class MonitorThread(Thread):
    def __init__(self, item, price, availability, purchase):
        self.item = item
        self.price = price
        self.availability = availability
        self.purchase = purchase
        super().__init__()

    def run(self):
        while True:
            if self.item.currentPrice <= self.price and self.item.isAvailable:
                # notify

                if self.purchase:
                    while True:
                        pass
                        # create checkout object
                        # purchase
                break


# class MyMeta(EnumMeta):
#     def __contains__(self, other):
#         if isinstance(other, int):
#             try:
#                 self(other)
#             except ValueError:
#                 return False
#             else:
#                 return True
#         elif isinstance(other, str):
#             try:
#                 self[other]
#             except KeyError:
#                 return False
#             else:
#                 return True
#         else:
#             return False


# class ROLES(Enum, metaclass=MyMeta):
#     admin = 1
#     purchase = 2
#     watch = 3
