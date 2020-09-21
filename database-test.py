import asyncio, datetime
from typing import Dict
from webscraper.server import db
from webscraper.server.database import (
    ProductBySellerModel,
    ProductModel,
    PriceHistoryModel,
    ProductWatchModel,
    SellerInfoModel,
)
from webscraper.models.user import UserModel
from webscraper.models.amazon import Amazon
from webscraper.models.bestbuy import BestBuy


async def checkPrices():

    # Check for duplicates in products
    product_ids = set(
        [
            product.product_id
            for product in ProductWatchModel.query.order_by(
                ProductWatchModel.product_id
            ).all()
        ]
    )

    # Create URL list
    products = []
    for id in product_ids:
        productsBySeller = ProductBySellerModel.query.filter_by(id=id).all()
        products.extend(productsBySeller)

    for product in products:
        url = product.seller.base_url + product.url_path

        model = None
        if "bestbuy" in url:
            model = await BestBuy.create(url)
        elif "amazon" in url:
            model = await Amazon.create(url)

        product.current_price = model.currentPrice

    db.session.commit()

    prices: Dict["id":"price"] = {}
    for product in products:
        # For duplicate products
        if product.id not in prices:
            prices[product.id] = product.current_price
        else:
            if prices[product.id] >= product.current_price:
                prices[product.id] = product.current_price

    for price in prices:
        db.session.add(
            SellerInfoModel(
                id=price, date_added=datetime.datetime.utcnow(), price=prices[price]
            )
        )

    db.session.commit()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(checkPrices())
