import requests
import re
from bs4 import BeautifulSoup
from modules.website import Website
import config


class Amazon(Website):

    @classmethod
    async def create(cls, url: str, currentPrice: float = None, regularPrice: float = None, title: str = None, generateWebObj: bool = True):
        self = Amazon(url, currentPrice, regularPrice, title)
        if generateWebObj:
            self.webObj = await self.generateWebObj()

        return self

    def __init__(self, url: str, currentPrice: float = None, regularPrice: float = None, title: str = None):
        super().__init__(url, config.AMAZON, currentPrice, regularPrice, title)

    @property
    def title(self) -> str:
        return super().getTitle().find(name="span", id="productTitle").getText().strip()

    @property
    def currentPrice(self) -> float:
        return float(
            re.findall(r"\d+\.?\d{0,2}", super().getCurrentPrice().get_text())[0].strip())

    @property
    def regularPrice(self) -> float:

        salePriceSpan = super().getRegularPrice()
        regPrice = self.currentPrice

        if salePriceSpan is not None:
            regPrice = float(re.findall(
                r"\d+\.?\d{0,2}", salePriceSpan.get_text())[0])

        return regPrice
