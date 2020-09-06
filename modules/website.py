from bs4 import BeautifulSoup
import requests
import re


class Website:
    def __init__(self, url: str, currentPriceDivAttr: dict, currentPriceAttr: dict, regularPriceDivAttr: dict, regularPriceAttr: dict, titleDivAttr: dict, titleAttr: dict, currentPrice: float = None, regularPrice: float = None, title: str = None, generateWebObj: bool = True):
        """Parent class for all websites

        Args:
            url (str): url of product
            currentPriceDivAttr (dict): attribute of div for current price component
            currentPriceAttr (dict): attribute of current price component
            regularPriceDivAttr (dict): attribute of div for regular price component
            regularPriceAttr (dict): attribute of regular price component
            titleDivAttr (dict): attribute of div for title component
            titleAttr (dict): attribute of title component
            currentPrice (float, optional): current price of product. Defaults to None.
            regularPrice (float, optional): regular price of product. Defaults to None.
            title (str, optional): title of product. Defaults to None.
            generateWebObj (bool, optional): whether to render and save website as beautifulsoup obj. Defaults to True.
        """
        self.currentPriceDivAttr = currentPriceDivAttr
        self.currentPriceAttr = currentPriceAttr
        self.reuglarPriceDivAttr = regularPriceDivAttr
        self.regularPriceAttr = regularPriceAttr
        self.titleDivAttr = titleDivAttr
        self.titleAttr = titleAttr
        self.url = url
        self.title = title
        self.currentPrice = currentPrice
        self.regularPrice = regularPrice

        self.webObj = Website.getWebsite(url) if generateWebObj else None

    @staticmethod
    def getWebsite(url: str) -> BeautifulSoup:
        """Renders the webpage into BeautifulSoup

        Args:
            url (str): url to render

        Returns:
            BeautifulSoup: rendered url object
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"}

        page = requests.get(url, headers=headers)

        assert page.ok, f"Website returned {page.status_code} error."

        return BeautifulSoup(page.content, 'html.parser')

    @staticmethod
    def getX(url: str, divAttr: dict, xAttr: dict, webObj: BeautifulSoup = None) -> BeautifulSoup:
        """Finds a certain component (x) by first finding the div with the right attribute(divAttr), then the component within the div with the right attribute(xAttr)

        Args:
            url (str): url to search
            divAttr (dict): attribute for the div
            xAttr (dict): attribute for the individual component

        Returns:
            BeautifulSoup: component matching given attributes
        """
        soup = webObj if webObj is not None else Website.getWebsite(url)

        div: BeautifulSoup = soup.find(name="div", attrs=divAttr)
        x: BeautifulSoup = div.find(attrs=xAttr)

        return x

    def getTitle(self) -> BeautifulSoup:
        """Returns the title component in BeautifulSoup

        Returns:
            BeautifulSoup: The title component
        """
        return Website.getX(self.url, self.titleDivAttr, self.titleAttr, self.webObj)

    def getCurrentPrice(self) -> BeautifulSoup:
        """Returns the price component in BeautifulSoup

        Returns:
            BeautifulSoup: The price component
        """
        return Website.getX(self.url, self.currentPriceDivAttr, self.currentPriceAttr, self.webObj)

    def getRegularPrice(self) -> BeautifulSoup:
        """Returns the regular price component in BeautifulSoup

        Returns:
            BeautifulSoup: The current price component, returns None if none exists
        """
        return Website.getX(self.url, self.reuglarPriceDivAttr, self.regularPriceAttr, self.webObj)

    def isOnSale(self) -> bool:
        """Checks whether product is currently on sale

        Returns:
            bool: True if product is on sale
        """
        return self.currentPrice < self.regularPrice
