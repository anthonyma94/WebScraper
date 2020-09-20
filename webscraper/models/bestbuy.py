import re
from webscraper.models.website import Website
from webscraper.config import BEST_BUY


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
        if generateWebObj:
            self.webObj = await self.generateWebObj()

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
            regPrice += float(re.findall(r"\d+", salePriceSpan.get_text())[0])

        return regPrice

    # def __str__(self):
    #     return f"""
    #     Best Buy Object
    #     -----------------------------
    #     Title: {self.title}
    #     Regular Price: {self.regularPrice}
    #     Current Price: {self.currentPrice}
    #     -----------------------------
    #     """
