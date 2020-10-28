from webscraper.models.bestbuy import BestBuy
from webscraper.models.products import PriceHistoryModel
from webscraper.utility.config import get_from_database
from webscraper.flask import app, db
import datetime


with app.app_context():

    item = BestBuy(
        "https://www.bestbuy.ca/en-ca/product/sony-wi-sp500-in-ear-bluetooth-headphones-with-mic-black/12545696"
    )

    def get_from_database(type, **kwargs):
        if not kwargs:
            return type.query.all()
        elif "id" in kwargs:
            return type.query.get(kwargs["id"])
        elif "func" in kwargs:
            return type.query.filter(kwargs["func"]).all()
        else:
            pass

    models = get_from_database(PriceHistoryModel)

    print(models)

    # models = PriceHistoryModel.query.all()

    # print(datetime.datetime.utcfromtimestamp(models[0].created_on))