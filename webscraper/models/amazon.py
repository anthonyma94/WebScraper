import re
from webscraper.models.website import Website
from webscraper.utility.utils import AMAZON


class Amazon(Website):
    def __init__(
        self,
        url: str,
    ):
        super().__init__(url, AMAZON)

    @property
    def name(self) -> str:
        return super().getName().find(name="span", id="productTitle").getText().strip()

    @property
    def currentPrice(self) -> float:
        return float(
            re.findall(r"\d+\.?\d{0,2}", super().getCurrentPrice().get_text())[
                0
            ].strip()
        )

    @property
    def regularPrice(self) -> float:

        salePriceSpan = super().getRegularPrice()
        regPrice = self.currentPrice

        if salePriceSpan is not None:
            regPrice = float(re.findall(r"\d+\.?\d{0,2}", salePriceSpan.get_text())[0])

        return regPrice
