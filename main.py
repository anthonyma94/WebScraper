from webscraper.api import api, app
from webscraper.public.routes import bp
from webscraper.api.routes import ProductApi, ProfileApi

if __name__ == "__main__":

    api.add_resource(ProductApi, "/api/products", "/api/products/<int:product_id>")
    api.add_resource(ProfileApi, "/api/profile")
    app.register_blueprint(bp)

    app.run()