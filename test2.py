from webscraper.models.bestbuy import BestBuy
from webscraper.models.products import PriceHistoryModel
from webscraper.flask import app, db
import datetime


with app.app_context():

    item = BestBuy(
        "https://www.bestbuy.ca/en-ca/product/sony-wi-sp500-in-ear-bluetooth-headphones-with-mic-black/12545696"
    )

    model = item.toDB()

    result = model.add_to_database()

    print(result)

    # models = PriceHistoryModel.query.all()

    # print(datetime.datetime.utcfromtimestamp(models[0].created_on))