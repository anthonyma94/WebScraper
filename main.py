from queue import Queue
from webscraper.models.tasks import MonitorThread
from webscraper.models.bestbuy import BestBuy
from webscraper.flask import api, app
from webscraper.flask.routes import bp
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
    app.register_blueprint(bp)

    # items = [
    #     BestBuy(
    #         "https://www.bestbuy.ca/en-ca/product/lenovo-smart-clock-essential-with-google-assistant-grey-cloth/14931829"
    #     ),
    #     # CanadaComputers(
    #     #     "https://www.canadacomputers.com/product_info.php?cPath=11_175_177&item_id=169562"
    #     # ),
    # ]

    # queue = Queue()
    # for i in range(len(items)):
    #     worker = MonitorThread(queue)
    #     # worker.daemon = True
    #     # print(worker)
    #     worker.start()

    # for i in items:
    #     queue.put(i)

    app.run()