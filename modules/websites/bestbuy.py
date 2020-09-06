from bs4 import BeautifulSoup
import re
import requests
from modules.website import Website


class BestBuy(Website):
    def __init__(self, url: str, currentPrice: float = None, regularPrice: float = None, title: str = None, generateWebObj: bool = True):
        currentPriceDivAttr = {"class": re.compile("^pricingContainer")}
        currentPriceAttr = {"itemprop": "price"}
        regularPriceAttr = {"class": re.compile(r"^productSaving")}
        titleDivAttr = {"class": "x-product-detail-page"}
        titleAttr = {"class": re.compile("^productName")}
        super().__init__(url, currentPriceDivAttr, currentPriceAttr, currentPriceDivAttr, regularPriceAttr,
                         titleDivAttr, titleAttr, currentPrice, regularPrice, title, generateWebObj)

        self.title = self.getTitle()
        self.currentPrice = self.getCurrentPrice()
        self.regularPrice = self.getRegularPrice()

    def getTitle(self) -> str:
        title = super().getTitle().get_text().strip()
        return title

    def getCurrentPrice(self) -> float:
        price = super().getCurrentPrice()
        price = float(price["content"])
        return price

    def getRegularPrice(self) -> float:
        salePriceSpan = super().getRegularPrice()
        regPrice = self.getCurrentPrice()

        if salePriceSpan is not None:
            regPrice += float(re.findall(r"\d+", salePriceSpan.get_text())[0])

        return regPrice
