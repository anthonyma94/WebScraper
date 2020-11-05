from queue import Queue
from webscraper.models.tasks import MonitorThread
from webscraper.models.bestbuy import BestBuy
from webscraper.flask import api, app
from webscraper.flask.routes import TaskApi, bp
from webscraper.flask.routes import HistoryApi, ProductApi, ProfileApi

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
    api.add_resource(HistoryApi, "/api/history", "/api/history/<int:id>")
    api.add_resource(TaskApi, "/api/task", "/api/tasks")
    app.register_blueprint(bp)

    app.run()