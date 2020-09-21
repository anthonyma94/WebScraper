from webscraper.models.amazon import Amazon
from webscraper.models.user import UserModel
from webscraper.server import addToDatabase, db, loop
from webscraper.server.database import (
    PriceHistoryModel,
    ProductModel,
    ProductBySellerModel,
    ProductWatchModel,
    SellerInfoModel,
)


if __name__ == "__main__":
    db.create_all()
    admin = UserModel(
        username="admin",
        password="Password1",
        email="admin@admin.com",
        public_id="admin",
        is_admin=True,
    )
    bestbuy = SellerInfoModel(name="Best Buy", base_url="https://bestbuy.ca/")
    amazon = SellerInfoModel(name="Amazon", base_url="https://amazon.ca/")
    amazon_product_url = "https://www.amazon.ca/ESR7Gears-Lighting-Detachable-Magnification-Tricolor/dp/B07NVHLCMR?smid=A3QT1YMIJJQJGH&pf_rd_r=VNDFZK7C1EQXT4E41V1E&pf_rd_p=0d7e2f33-cd4a-4e33-8cdd-00535c3c3f76"
    items = []

    if not UserModel.query.filter_by(username="admin").first():
        items.append(admin)

    if not SellerInfoModel.query.filter_by(name="Best Buy").first():
        items.append(bestbuy)

    if not SellerInfoModel.query.filter_by(name="Amazon").first():
        items.append(amazon)

    addToDatabase(items)
    amazon_product_class = loop.run_until_complete(Amazon.create(amazon_product_url))
    amazon_product = ProductModel(name=amazon_product_class.title)
    addToDatabase(amazon_product)

    amazon_productWatch = ProductWatchModel(
        user_id=admin.public_id, product_id=amazon_product.id
    )

    amazon_productSeller = ProductBySellerModel(
        id=amazon_product.id,
        seller_id=SellerInfoModel.query.filter_by(name="Amazon").first().id,
        url_path=amazon_product_class.url_path,
        current_price=amazon_product_class.currentPrice,
    )

    addToDatabase([amazon_productSeller, amazon_productWatch])