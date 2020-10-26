from webscraper.api import api, app
from webscraper.api.routes import ProductApi

if __name__ == "__main__":
    api.add_resource(ProductApi, "/api/products", "/api/products/<int:product_id>")
    app.run()