from webscraper.utility.utils import db, add_to_database
from sqlalchemy import and_
from threading import Thread
import time


class TaskModel(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.Integer, db.ForeignKey("products.id"))
    price_limit = db.Column(db.Float)
    purchase = db.Column(db.Boolean, default=False)
    notify_on_available = db.Column(db.Boolean, default=True)

    def add_to_database(self, **kwargs):
        return add_to_database(
            self,
            TaskModel.query.filter(TaskModel.postal_code == self.product).first(),
            **kwargs,
        )


class MonitorThread(Thread):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def run(self):
        item = self.queue.get()
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