from itertools import product
from operator import itemgetter
from webscraper.models.products import ProductModel

from sqlalchemy.exc import DatabaseError
from webscraper.models.profiles import ProfileModel
from sqlalchemy.orm import query_expression
from enum import unique
from webscraper.utility.utils import db, add_to_database, get_from_database
from sqlalchemy import and_
from threading import Thread
import time
import flask


class TaskModel(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.Integer, db.ForeignKey("products.id"), unique=True)
    price_limit = db.Column(db.Float)
    purchase = db.Column(db.Boolean, default=False)
    notify_on_available = db.Column(db.Boolean, default=True)
    profile = db.Column(db.Integer, db.ForeignKey("profiles.id"))
    current_price = db.Column(db.Float)
    def add_to_database(self, **kwargs):
        return add_to_database(
            self,
            TaskModel.query.filter(TaskModel.postal_code == self.product).first(),
            **kwargs,
        )

class Task():
    
    def __init__(self, product, price_limit, purchase, notify_on_available, item):
            self.price_limit = price_limit,
            self.purchase = purchase,
            self.notify_on_available = notify_on_available,
            self.item = item,
            self.profile = profile

class MonitorThread(Thread):
    def __init__(self, queue):
        super().__init__()
        
        try:
            self.tasks = get_from_database(TaskModel)
        except DatabaseError:
            print("Almost made it, error ")
        self.previousState = []

        def getProfileDB(self, profileID):
            return get_from_database(ProfileModel, profileID)

        def getProduct(self, productID):
            return get_from_database(ProductModel, productID)
        
        def iterTasks():
            while True:
                for task in self.tasks:
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