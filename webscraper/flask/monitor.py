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
from win10toast import ToastNotifier

class MonitorThread(Thread):
    def __init__(self):
        super().__init__()
        self.tn = ToastNotifier()
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
                with app.app_context():
                    product = get_from_database(ProductModel, **{"id" : task.product})
                    # if product.getCurrentPrice() <= task.price_limit:
                    #     print(product.getAvailability())
                    
            return False
    def run(self):
        print("print Thread is running POG")
        print(self.tasks)
        while True:
            with app.app_context():
                self.iterTasks()
            self.tn.show_toast("Update from Scraper", "big ol message", icon_path="webscraper\\flask\\favicon.ico")
            break
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