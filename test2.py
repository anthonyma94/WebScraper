import time

from flask_sqlalchemy import model
from webscraper.models.tasks import TaskModel
from webscraper.models.cc import CanadaComputers
import regex
from queue import Queue
from webscraper.models.profiles import CreditCardModel, ProfileModel, ShoppingProfile
from webscraper.models.bestbuy import BestBuy
from webscraper.models.products import ProductModel
from webscraper.utility.utils import get_from_database, update_database
from webscraper.flask import app, db
import datetime

with app.app_context():
    item = get_from_database(TaskModel, id=1)
    item.current_price = 5

    db.session.commit()
    # item = update_database(item, id=1)

    # print(item.current_price)
# queue.join()

# item = BestBuy(
#     "https://www.bestbuy.ca/en-ca/product/lenovo-smart-clock-essential-with-google-assistant-grey-cloth/14931829"
# )

# itemStart = time.perf_counter()
# item.getAvailability()
# print(f"Price time: {time.perf_counter() - itemStart}s.")


# items = [
#     BestBuy(
#         "https://www.bestbuy.ca/en-ca/product/lenovo-smart-clock-essential-with-google-assistant-grey-cloth/14931829"
#     ),
#     # CanadaComputers(
#     #     "https://www.canadacomputers.com/product_info.php?cPath=11_175_177&item_id=169562"
#     # ),
# ]

# if __name__ == '__main__':

#     for i in range(len(items)):
#         worker = MonitorThread()
#         worker.start()

#     for i in items:
