import regex
from webscraper.models.profiles import CreditCardModel
from webscraper.models.bestbuy import BestBuy
from webscraper.models.products import PriceHistoryModel, ProductModel
from webscraper.utility.utils import get_from_database
from webscraper.flask import app, db
import datetime

url = "https://www.bestbuy.ca/en-ca/product/sony-wi-sp500-in-ear-bluetooth-headphones-with-mic-black/1254569624562345398457/wertioughuwyadfjlakjsrbgoqairweeasitrpohgqeyauwrogf;/8-0=-=-ljaskdfga;dslkf?><++===/.alks;dfgj;lkj"

match = regex.match(r"^https:\/\/www\.bestbuy\.ca\/en-ca\/product\/.*(\d{8}).*$", url)

url = regex.sub(r"(?<=\d{8}).*$", "", url)

print(url)


# with app.app_context():

#     #     item = BestBuy(
#     #         "https://www.bestbuy.ca/en-ca/product/sony-wi-sp500-in-ear-bluetooth-headphones-with-mic-black/12545696"
#     #     )

#     #     def get_from_database(type, **kwargs):
#     #         if not kwargs:
#     #             return type.query.all()
#     #         elif "id" in kwargs:
#     #             return type.query.get(kwargs["id"])
#     #         elif "func" in kwargs:
#     #             return type.query.filter(kwargs["func"]).all()
#     #         else:
#     #             pass

#     #     models = get_from_database(PriceHistoryModel)

#     #     print(models)

#     models = get_from_database(CreditCardModel, id=1)
#     print(models.__dict__)

# models = PriceHistoryModel.query.all()

# print(datetime.datetime.utcfromtimestamp(models[0].created_on))
