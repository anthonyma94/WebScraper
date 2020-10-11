import webscraper.errors as error
from webscraper.models.user import UserModel
from webscraper.models.products import (
    ProductModel,
    ProductWatchModel,
    PriceHistoryModel,
)
from webscraper.models.bestbuy import BestBuy
from webscraper.config import db
from sqlalchemy.exc import IntegrityError


def addProductToDatabase(user: UserModel, url=None, item: ProductModel = None) -> bool:
    if (url is None and item is None) or (url is not None and item is not None):
        raise error.IncorrectInfoException

    if url is not None:
        if "bestbuy" in url:
            item = BestBuy(url).toDB()

    try:
        db.session.add(item)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        db.session.flush()
        item = ProductModel.query.filter_by(url=item.url).first()

    watch = ProductWatchModel(user_id=user.id, product_id=item.id)
    try:
        db.session.add(watch)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        db.session.flush()
        raise error.InternalServerException("Product watch already exists for user.")

    product = None
    if "bestbuy" in item.url:
        product = BestBuy.fromDB(item)

    history = PriceHistoryModel(
        id=item.id,
        price=product.currentPrice,
        is_available=product.isAvailable,
    )
    db.session.add(history)
    db.session.commit()