import time
from time import sleep
import os
from webscraper.flask.routes import profile
from Crypto.Cipher.PKCS1_OAEP import new
import flask
import copy
from webscraper.flask import app
from sqlalchemy import and_
from threading import Thread
from sqlalchemy.orm import query_expression
from enum import unique
from sqlalchemy.exc import DatabaseError
from webscraper.models.profiles import ProfileModel
from itertools import product
from operator import itemgetter
from webscraper.utility.utils import BEST_BUY, db, add_to_database, get_from_database, update_database, delete_from_database
from webscraper.models.products import ProductModel
from webscraper.models.tasks import TaskModel
from win10toast import ToastNotifier
from webscraper.models.bestbuy import BestBuy, BestBuyCheckOut
from webscraper.models.cc import CanadaComputers, CanadComputersCheckout


class MonitorThread(Thread):
    def __init__(self):
        super().__init__()
        self.tn = ToastNotifier()
        self.bb = "bestbuy"
        self.cc = "canadacomputer"
        try:
            with app.app_context():
                self.tasks = get_from_database(TaskModel)
        except DatabaseError:
            print("Almost made it, error ")
        self.previousState = []

    def getProfileDB(self, profileID):
        return get_from_database(ProfileModel, profileID)

    def getProduct(self, productID) -> ProductModel:
        return get_from_database(ProductModel, productID)
    
    def iterTasks(self) -> None:
        while True:
            for task in self.tasks:
                if task.completed:
                    continue
                with app.app_context():
                    product = get_from_database(ProductModel, **{"id" : task.product})
                    supplier = BestBuy if self.bb in product.url else CanadaComputers
                    controller = supplier(product.url)
                    if newPrice:=controller.getCurrentPrice() <= task.price_limit:
                        
                        if task.purchase and controller.getAvailability():
                            pp = get_from_database(ProfileModel, **{"id" : task.profile})
                            shopper = BestBuyCheckOut(profile = pp, item = controller)
                            checkedOut = shopper.checkout()
                            checkedOutMssg = f"Successfully purchases {product.name} from {' Best Buy' if supplier == self.bb else ' Canada Computers'}. Your order number is {checkedOut}" if checkedOut else f"Purchase of {product.name} failed"
                            self.tn.show_toast(f"Purchase Update", checkedOutMssg, icon_path="webscraper\\flask\\favicon.ico")
                            continue

                        if newPrice != task.current_price:
                            self.tn.show_toast( f"{product.name} Price Updated",
                                                f"{product.name} changed from ${task.getCurrentPrice} to ${newPrice}",
                                                icon_path="webscraper\\flask\\favicon.ico")
                            newTask = copy.deepcopy(task)
                            newTask.getCurrentPrice = newPrice
                            update_database(task, newTask)
                            print("database Updated")

                            
                    # if product.getCurrentPrice() <= task.price_limit:
                    #     print(product.getAvailability()) 
    def run(self):
        print("print Thread is running POG")
        print(self.tasks)
        interval = os.getenv('SCRAPE_INTERVAL')
        while True:
            with app.app_context():
                self.iterTasks()
                self.tasks = self.tasks = get_from_database(TaskModel)
                sleep(interval)
                
            # self.tn.show_toast("Update from Scraper", "big ol message", icon_path="webscraper\\flask\\favicon.ico")
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