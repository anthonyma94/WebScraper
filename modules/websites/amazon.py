import requests
import re
from bs4 import BeautifulSoup
from modules.website import Website


class Amazon(Website):
    def __init__(self, url: str, currentPrice: float = None, regularPrice: float = None, title: str = None, generateWebObj: bool = True):
        currentPriceDivAttr = {"id": "price"}
        currentPriceAttr = {"id": re.compile(
            r"^priceblock_ourprice$|^priceblock_dealprice$")}
        regularPriceAttr = {"class": "priceBlockStrikePriceString"}
        titleDivAttr = {"id": "titleSection"}
        titleAttr = {"id": "productTitle"}

        super().__init__(url, currentPriceDivAttr, currentPriceAttr, currentPriceDivAttr,
                         regularPriceAttr, titleDivAttr, titleAttr, currentPrice, regularPrice, title)

        self.title = self.getTitle()
        self.currentPrice = self.getCurrentPrice()
        self.regularPrice = self.getRegularPrice()

    def getTitle(self) -> str:
        self.title = super().getTitle().get_text().strip()
        return self.title

    def getCurrentPrice(self) -> float:
        self.currentPrice = float(
            re.findall(r"\d+\.?\d{0,2}", super().getCurrentPrice().get_text())[0].strip())
        return self.currentPrice

    def getRegularPrice(self) -> float:

        salePriceSpan = super().getRegularPrice()
        regPrice = self.getCurrentPrice()

        if salePriceSpan is not None:
            regPrice = float(re.findall(
                r"\d+\.?\d{0,2}", salePriceSpan.get_text())[0])

        return regPrice
