from webscraper.config import CANADACOMPUTERS
from webscraper.models.website import Website
from webscraper.models.products import ProductModel
import webscraper.errors as error
import regex, requests
from lxml import html


class CanadaComputers(Website):
    def __init__(self, url):
        match = regex.match(
            r"^https:\/\/www\.canadacomputers\.com\/product_info\.php\?.*item_id=(\d{6})$",
            url,
        )
        if match is None:
            raise error.IncorrectInfoException

        super().__init__(url=url, attributes=CANADACOMPUTERS, sku=int(match.group(1)))

    @property
    def name(self):
        return super().getTitle().get_text().strip()

    @property
    def currentPrice(self) -> float:
        price = super().getCurrentPrice().get_text().strip()
        return float(price[1:])

    @property
    def regularPrice(self) -> float:
        price = super().getRegularPrice()

        if price is not None:
            price = float(price.get_text().replace("Was:", "").strip()[1:])
        return price

    @property
    def isAvailable(self) -> bool:
        return super().getAvailability() is not None

    @property
    def imageURL(self) -> str:
        return super().getImage()["src"]

    @staticmethod
    def fromDB(product: ProductModel):
        return CanadaComputers(product.url)

    def toDB(self) -> ProductModel:
        return ProductModel(
            sku=self.sku, url=self.url, name=self.name, image_url=self.imageURL
        )
