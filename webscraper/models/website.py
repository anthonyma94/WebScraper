import regex

import aiohttp as http
from bs4 import BeautifulSoup


class Website:
    async def generateWebObj(self) -> BeautifulSoup:
        return await Website.getWebsite(self.url)

    def __init__(
        self,
        url: str,
        attributes: dict,
        currentPrice: float = None,
        regularPrice: float = None,
        title: str = None,
    ):
        """Parent class for all websites

        Args:
            url (str): url of product
            attributes (dict): attributes of website as set in config.py.
            currentPrice (float, optional): current price of product. Defaults to None.
            regularPrice (float, optional): regular price of product. Defaults to None.
            title (str, optional): title of product. Defaults to None.
        """
        self.attributes = attributes
        self.url = url
        self.webObj = None
        # self.currentPrice = currentPrice
        # self.regularPrice = regularPrice

        # print(self.attributes)

    @staticmethod
    async def getWebsite(url: str) -> BeautifulSoup:
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

        async with http.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                assert (
                    response.status < 400
                ), f"Website returned {response.status} error."
                return BeautifulSoup(await response.content.read(), "html.parser")

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

        # print(divAttr)
        # print(xAttr)

        soup = webObj

        div: BeautifulSoup = soup.find(name="div", attrs=divAttr)
        x: BeautifulSoup = div.find(attrs=xAttr)

        return x

    @property
    def url_path(self) -> str:
        return regex.findall(r"(?<=\.com\/|\.ca\/)(.*)", self.url)[0].strip()

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

    def __str__(self):
        return f"""
{self.__class__.__name__} Object
-----------------------------
Title: {self.title}
Regular Price: {self.regularPrice}
Current Price: {self.currentPrice}
-----------------------------
"""
