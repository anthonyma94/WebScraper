import time
import flask
from webscraper.flask import app
from sqlalchemy import and_
from threading import Thread
from sqlalchemy.orm import query_expression
from enum import unique
from sqlalchemy.exc import DatabaseError
from webscraper.models.profiles import ProfileModel
from itertools import product
from operator import itemgetter
from webscraper.utility.utils import db, add_to_database, get_from_database
from webscraper.models.products import ProductModel
from webscraper.models.tasks import TaskModel


class Task():
    
    def __init__(self, product, price_limit, purchase, notify_on_available, item):
            self.price_limit = price_limit,
            self.purchase = purchase,
            self.notify_on_available = notify_on_available,
            self.item = item,
            self.profile = profile

class MonitorThread(Thread):
    def __init__(self):
        super().__init__()
        
        try:
            with app.app_context():
                self.tasks = get_from_database(TaskModel)
        except DatabaseError:
            print("Almost made it, error ")
        self.previousState = []

    def getProfileDB(self, profileID):
        return get_from_database(ProfileModel, profileID)

    def getProduct(self, productID):
        return get_from_database(ProductModel, productID)
    
    def iterTasks(self):
        while True:
            for task in self.tasks:
                # self.tasks.getProduct()
                pass

    def run(self):
        print("print Thread is running POG")
        print(self.tasks)
        while True:
            with app.app_context():
                pass

    # def updateItems(self, itemQueue):
    #     while not itemQueue.empty():
    #         self.items.append(itemQueue.get())
    #         itemQueue.task_done()

    # def isUnderPrice(self, item):
    #     return item.getCurrentPrice() <= item.price_limit

    # def isAvailable(self, item):
    #     return item.getAvailability()
    
    
    # def run(self):
        
    #     while True:
    #         for item in self.items:
    #             price = item.getCurrentPrice()
    #             availability = item.getAvailability()
                
    #             print(f"{item.name}: ${price}")

    #             # if price <= self.priceLimit and availability:
    #             #     # notify

    #             #     if self.purchase:
    #             #         while True:
    #             #             pass
    #             #             # create checkout object
    #             #             # purchase
    #             #     break

    #             time.sleep(1)



#     def __repr__(self) -> str:
#         return str(self.__dict__)


# def testFunction():
    

#     monitor = MonitorThread()