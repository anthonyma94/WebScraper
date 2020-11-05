from itertools import product
from sqlalchemy.orm import query_expression
from enum import unique
from webscraper.utility.utils import db, add_to_database
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

    def add_to_database(self, **kwargs):
        return add_to_database(
            self,
            TaskModel.query.filter(TaskModel.postal_code == self.product).first(),
            **kwargs,
        )

class Task():
    
    def __init__(self, id, product, price_limit, purchase, notify_on_available):
        self.id = id
        self.product = product
        self.price_limit = price_limit
        self.purchase = purchase
        self.notify_on_available = notify_on_available

class MonitorThread(Thread):
    def __init__(self, queue):
        super().__init__()
        self.items = []
        self.previousState = []
    
    def updateItems(self, itemQueue):
        while not itemQueue.empty():
            self.items.append(itemQueue.get())
            itemQueue.task_done()

    def isUnderPrice(self, item):
        return item.getCurrentPrice() <= item.price_limit

    def isAvailable(self, item):
        return item.getAvailability()
    
    
    def run(self):
        
        while True:
            # print(f"Running: {item.url}")
            price = item.getCurrentPrice()
            availability = item.getAvailability()
            
            print(f"{item.name}: ${price}")

            # if price <= self.priceLimit and availability:
            #     # notify

            #     if self.purchase:
            #         while True:
            #             pass
            #             # create checkout object
            #             # purchase
            #     break

            time.sleep(1)



    def __repr__(self) -> str:
        return str(self.__dict__)


def testFunction():
    

    monitor = MonitorThread()