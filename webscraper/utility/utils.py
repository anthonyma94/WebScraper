import json
import random
import re, time
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
    """
    Adds given item to database

    Args:
        item (Model): Any Flask-SQLAlchemy model item
        func (function): Query function if item is already in database

    Kwargs:
        silent (Boolean): Whether to throw IntegrityError

    Raises:
        e: IntegrityError if silent is false

    Returns:
        Model: The item that is either added to database or queried from func
    """

    if item.id is not None and item.id != "":
        if type(item).query.get(item.id) is not None:
            if "silent" in kwargs and not kwargs["silent"]:
                raise IntegrityError("Item already exists.")
            return item

    try:
        db.session.add(item)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # db.session.flush()
        if "silent" in kwargs and not kwargs["silent"]:
            raise e
        item = func
    return item


def get_from_database(type, **kwargs):
    """
    Retrieves item from database

    Args:
        type (Model): Any Flask-SQLAlchemy model class

    Kwargs:
        Any kwargs is valid given it is a valid query for the class
        id (Any): id of item to retrieve
        filter (function): query function to call for item

    Raises:
        e: AttributeError if given kwargs does not exist for class

    Returns:
        Model: item based on given kwarg queries
    """
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


def update_database(old, new):
    # def update_database(type, id, kwargs):
    """
    Updates item in database

    Args:
        item (Model): Any Flask-SQLAlchemy model class

    Kwargs:
        Any attributes to update

    Raises:
        e: Any exception given when trying to update item

    Returns:
        Model: Updated item
    """

    if type(old) is not type(new):
        raise Exception("Must be the same type")

    changes = new.__dict__
    changes.pop("_sa_instance_state")

    changed = False

    try:
        for key in changes:
            if str(getattr(old, key)) != str(changes[key]):
                setattr(old, key, changes[key])
                changed = True

        if changed:
            db.session.commit()
    except Exception as e:
        raise e

    return old


def getUA():
    try:
        with open("user-agents.json", "r") as f:
            x = json.load(f)
            ua = x[random.randint(0, len(x) - 1)]
    except:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"

    return ua


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
