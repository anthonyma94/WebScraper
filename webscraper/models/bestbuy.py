import regex
from webscraper.models.website import Website
from webscraper.config import BEST_BUY
from bs4 import BeautifulSoup
import requests


class BestBuy(Website):
    def __init__(
        self,
        url: str,
        currentPrice: float = None,
        regularPrice: float = None,
        title: str = None,
    ):
        super().__init__(
            url,
            BEST_BUY,
            currentPrice=currentPrice,
            regularPrice=regularPrice,
            title=title,
        )

    @classmethod
    async def create(
        cls,
        url: str,
        currentPrice: float = None,
        regularPrice: float = None,
        title: str = None,
        generateWebObj: bool = True,
    ):
        self = BestBuy(url, currentPrice, regularPrice, title)
        if generateWebObj:  # submits get request synchronously because it's faster
            resp = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
                },
            )
            self.webObj = BeautifulSoup(resp.content, "html.parser")

        return self

    @property
    def title(self) -> str:
        return super().getTitle().get_text().strip()

    @property
    def currentPrice(self) -> float:
        return float((super().getCurrentPrice())["content"])

    @property
    def regularPrice(self) -> float:
        salePriceSpan = super().getRegularPrice()
        regPrice = self.currentPrice

        if salePriceSpan is not None:
            regPrice += float(regex.findall(r"\d+", salePriceSpan.get_text())[0])

        return regPrice
