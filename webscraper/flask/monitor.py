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
from webscraper.models.profiles import ProfileModel, ShoppingProfile
from itertools import product
from operator import itemgetter
from webscraper.utility.utils import (
    BEST_BUY,
    db,
    add_to_database,
    get_from_database,
    update_database,
    delete_from_database,
)
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
    def retryTransaction(self, shopper):
        count = 0
        purchased = False
        results = None
        while purchased == False or count < 3:
            try:
                results = shopper.checkout()
            except Exception:
                count += 1
            purchased = True
        return results
    def iterTasks(self):
        for task in self.tasks:
            print(f"Iterating over task {1}")
            if task.completed:
                continue
            # with app.app_context():
            product = get_from_database(ProductModel, **{"id": task.product})
            supplier = BestBuy if self.bb in product.url else CanadaComputers
           
            controller = supplier(product.url)
            newPrice = controller.getCurrentPrice()
            if newPrice <= task.price_limit:
    
                if task.purchase and controller.getAvailability():
                    pp = get_from_database(ProfileModel, **{"id": task.profile})
                    sp =  ShoppingProfile.fromDB(pp)
                    shopper = BestBuyCheckOut(profile=sp, item=controller)
                    try:
                        checkedOut = shopper.checkout()
                        checkMssg = (f"Successfully purchases {product.name} from {' Best Buy' if supplier == self.bb else ' Canada Computers'}. Your order number is {checkedOut}")
                    except Exception as e:
                        purchase_attempts = 1
                        if e == 400:
                            update_database(TaskModel, task.id, completed=True)
                            checkMssg = (f"Transaction Failed: Credit Card Failed \n Please check card profile information on profile for {pp.email}")
                        else:
                            failure = "We attempted to purchase 3 times, but failed"
                            checkedOut = self.retryTransaction(shopper)
                            if not checkedOut:
                                checkMssg = (f"Transaction Failed: {failure}")
                                update_database(TaskModel, task.id, completed=True)
                        
                    self.tn.show_toast(
                        f"Purchase Update for {product.name}",
                        checkMssg,
                        icon_path="webscraper\\flask\\favicon.ico",
                    )
                    if checkedOut:
                        update_database(TaskModel, task.id, completed=True)

            if newPrice != task.current_price or task.current_price is None:
                self.tn.show_toast(
                    f"{product.name} Price Updated",
                    f"{product.name} changed from ${task.current_price} to ${newPrice}",
                    icon_path="webscraper\\flask\\favicon.ico",
                )
                # newTask = copy.deepcopy(task)
                # newTask.current_price = newPrice
                # update_database(task, newTask)

                update_database(TaskModel, task.id, current_price=newPrice)
                # update_database(new=task, id=task.id)

                print("database Updated")

                # if product.getCurrentPrice() <= task.price_limit:
                #     print(product.getAvailability())

    def run(self):
        print("print Thread is running POG")
        print(self.tasks)
        interval = os.getenv("SCRAPE_INTERVAL")
        while True:
            with app.app_context():
                self.iterTasks()
                self.tasks = self.tasks = get_from_database(TaskModel)
                sleep(int(interval))

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