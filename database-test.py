from webscraper.server import db
from webscraper.server.database import (
    ProductBySellerModel,
    ProductModel,
    PriceHistoryModel,
)

if __name__ == "__main__":
    product = ProductModel.query.first()

    seller = ProductBySellerModel.query.first()

    print(product.seller[0].current_price)
