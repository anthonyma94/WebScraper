from webscraper.api import api, app
from webscraper.public.routes import bp
from webscraper.api.routes import ProductApi

if __name__ == "__main__":

    api.add_resource(ProductApi, "/api/products", "/api/products/<int:product_id>")
    app.register_blueprint(bp)
    app.run()