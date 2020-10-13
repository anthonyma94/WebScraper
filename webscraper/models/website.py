import regex, requests
from bs4 import BeautifulSoup


class Website:
    async def generateWebObj(self) -> BeautifulSoup:
        return await Website.getWebsite(self.url)

    def __init__(
        self,
        url: str,
        attributes: dict,
        sku: int = None,
        currentPrice: float = None,
        regularPrice: float = None,
        webObj: bool = True,
    ):
        """Parent class for all websites

        Args:
            url (str): url of product
            attributes (dict): attributes of website as set in config.py.
            sku (int, optional): sku of product relative to its company. Defaults to None.
            currentPrice (float, optional): current price of product. Defaults to None.
            regularPrice (float, optional): regular price of product. Defaults to None.
            title (str, optional): title of product. Defaults to None.
        """
        self.attributes = attributes
        self.url = url
        if sku is not None:
            self.sku = sku
        if currentPrice is not None:
            self.currentPrice = currentPrice
        if regularPrice is not None:
            self.regularPrice = regularPrice
        if webObj:
            self.webObj = Website.getWebsite(self.url)

    @staticmethod
    def getWebsite(url: str) -> BeautifulSoup:
        """Renders the webpage into BeautifulSoup

        Args:
            url (str): url to render
            session (aiohttp.ClientSession): session to use

        Returns:
            BeautifulSoup: rendered url object
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"
        }

        res = requests.get(url, headers=headers)
        assert res.ok, f"Website returned {res.reason} error."

        return BeautifulSoup(res.content, "html.parser")

    @staticmethod
    def getX(webObj: BeautifulSoup, divAttr: dict, xAttr: dict) -> BeautifulSoup:
        """Finds a certain component (x) by first finding the div with the right attribute(divAttr), then the component within the div with the right attribute(xAttr)

        Args:
            webObj (BeautifulSoup): BeautifulSoup object of rendered webpage
            divAttr (dict): attribute for the div
            xAttr (dict): attribute for the individual component

        Returns:
            BeautifulSoup: component matching given attributes
        """

        soup = webObj

        div: BeautifulSoup = soup.find(name="div", attrs=divAttr)
        x: BeautifulSoup = div.find_next(attrs=xAttr)

        return x

    def getTitle(self) -> BeautifulSoup:
        """Returns the title component in BeautifulSoup

        Returns:
            BeautifulSoup: The title component
        """
        return Website.getX(
            self.webObj, self.attributes["titleDivAttr"], self.attributes["titleAttr"]
        )

    def getCurrentPrice(self) -> BeautifulSoup:
        """Returns the price component in BeautifulSoup

        Returns:
            BeautifulSoup: The price component
        """
        return Website.getX(
            self.webObj,
            self.attributes["currentPriceDivAttr"],
            self.attributes["currentPriceAttr"],
        )

    def getRegularPrice(self) -> BeautifulSoup:
        """Returns the regular price component in BeautifulSoup

        Returns:
            BeautifulSoup: The current price component, returns None if none exists
        """
        return Website.getX(
            self.webObj,
            self.attributes["regularPriceDivAttr"],
            self.attributes["regularPriceAttr"],
        )

    def isOnSale(self) -> bool:
        """Checks whether product is currently on sale

        Returns:
            bool: True if product is on sale
        """
        return self.currentPrice < self.regularPrice

    def getAvailability(self) -> BeautifulSoup:
        return Website.getX(
            self.webObj,
            self.attributes["availabilityDivAttr"],
            self.attributes["availabilityAttr"],
        )

    def getImage(self) -> BeautifulSoup:
        return Website.getX(
            self.webObj,
            self.attributes["imageDivAttr"],
            self.attributes["imageAttr"],
        )

    def __repr__(self):
        return f"""
{self.__class__.__name__} Object
-----------------------------
Title: {self.title}
Regular Price: {self.regularPrice}
Current Price: {self.currentPrice}
-----------------------------
"""
