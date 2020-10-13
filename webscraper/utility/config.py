import re
from flask_sqlalchemy import SQLAlchemy
from enum import Enum, EnumMeta, IntEnum

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


class MyMeta(EnumMeta):
    def __contains__(self, other):
        if isinstance(other, int):
            try:
                self(other)
            except ValueError:
                return False
            else:
                return True
        elif isinstance(other, str):
            try:
                self[other]
            except KeyError:
                return False
            else:
                return True
        else:
            return False


class ROLES(Enum, metaclass=MyMeta):
    admin = 1
    purchase = 2
    watch = 3
