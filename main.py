from itertools import product
from webscraper.models.tasks import TaskModel
from webscraper.models.products import ProductModel
from webscraper.flask import api, app
from webscraper.flask.routes import TaskApi, bp, profile
from webscraper.flask.routes import ProductApi, ProfileApi
from webscraper.flask.monitor import MonitorThread
from webscraper.utility.utils import db, add_to_database, get_from_database
import requests
from flask import Flask
import threading
import time

@app.before_first_request
def activate_job():
    thread = MonitorThread()
    thread.start()


def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print("In start loop")
            try:
                r = requests.get("http://127.0.0.1:5000/")
                if r.status_code == 200:
                    print("Server started, quiting start_loop")
                    not_started = False
                print(r.status_code)
            except:
                print("Server not yet started")
            time.sleep(2)

    print("Started runner")
    thread = threading.Thread(target=start_loop)
    thread.start()


if __name__ == "__main__":

    api.add_resource(
        ProductApi,
        "/api/product",
        "/api/product/<int:product_id>",
        "/api/products",
        "/api/products/<int:product_id>",
    )
    api.add_resource(
        ProfileApi,
        "/api/profile",
        "/api/profile/<int:id>",
        "/api/profiles",
        "/api/profiles/<int:id>",
    )

    # api.add_resource(HistoryApi, "/api/history", "/api/history/<int:id>")
    api.add_resource(
        TaskApi, "/api/task", "/api/task/<int:id>", "/api/tasks/<int:id>", "/api/tasks"
    )
    app.register_blueprint(bp)
    # mt = MonitorThread()
    # mt.run()

    # mt = MonitorThread()
    # get_from_database(ProductModel)
    start_runner()
    app.run()