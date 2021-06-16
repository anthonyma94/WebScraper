from webscraper.utility.utils import getUA
import webscraper.utility.errors as error
import regex, requests
from bs4 import BeautifulSoup


class Website:
    def generateWebObj(self) -> BeautifulSoup:
        return Website.getWebsite(self.url)

    headers = {"User-Agent": getUA()}

    def __init__(
        self,
        url: str,
        attributes: dict,
        sku: int = None,
        webObj: bool = True,
    ):
        """Parent class for all websites

        Args:
            url (str): url of product
            attributes (dict): attributes of website as set in config.py.
            sku (int, optional): sku of product relative to its company. Defaults to None.
        """
        if webObj:
            try:
                self.webObj = Website.getWebsite(url)
            except AssertionError as e:
                raise error.NotFoundException
        else:
            res = requests.get(url, headers=Website.headers)
            if res.status_code == 404:
                raise error.NotFoundException
            elif not res.ok:
                raise error.InternalServerException("An unknown error occured.")

        self.attributes = attributes
        self.url = url
        if sku:
            self.sku = sku

    @staticmethod
    def getWebsite(url: str) -> BeautifulSoup:
        """Renders the webpage into BeautifulSoup

        Args:
            url (str): url to render
            session (aiohttp.ClientSession): session to use

        Returns:
            BeautifulSoup: rendered url object
        """

        res = requests.get(url, headers=Website.headers)
        if not res.ok:
            raise Exception(f"Website returned {res.reason} error.")

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

    def getName(self) -> BeautifulSoup:
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
        return self.getCurrentPrice() < self.getRegularPrice()

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
Name: {self.name}
URL: {self.url}
SKU: {self.sku}
Regular Price: {self.getRegularPrice()}
Current Price: {self.getCurrentPrice()}
-----------------------------
"""
