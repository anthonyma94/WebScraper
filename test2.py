import time
from webscraper.models.tasks import MonitorThread
from webscraper.models.cc import CanadaComputers
import regex
from queue import Queue
from webscraper.models.profiles import CreditCardModel
from webscraper.models.bestbuy import BestBuy
from webscraper.models.products import PriceHistoryModel, ProductModel
from webscraper.utility.utils import get_from_database
from webscraper.flask import app, db
import datetime


# queue.join()

# item = BestBuy(
#     "https://www.bestbuy.ca/en-ca/product/lenovo-smart-clock-essential-with-google-assistant-grey-cloth/14931829"
# )

# itemStart = time.perf_counter()
# item.getAvailability()
# print(f"Price time: {time.perf_counter() - itemStart}s.")