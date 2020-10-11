import regex, json, requests
import webscraper.errors as error
from typing import Dict
from webscraper.models.website import Website
from webscraper.models.products import ProductModel
from webscraper.config import BEST_BUY


class BestBuy(Website):
    def __init__(self, url):
        match = regex.match(
            r"^https:\/\/www\.bestbuy\.ca\/en-ca\/product\/.*(\d{8})$", url
        )
        if match is None:
            raise error.IncorrectInfoException("Incorrect URL.")

        super().__init__(url, BEST_BUY, sku=int(match.group(1)), webObj=False)
        self.json = self.getJSON()

    def getJSON(self) -> Dict:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        }
        url = f"https://www.bestbuy.ca/api/v2/json/product/{self.sku}"
        res = requests.get(url, headers=headers)
        if not (res.ok):
            raise error.BadRequestException(
                f"Could not retrieve JSON, {res.reason} ({res.status_code})"
            )

        return res.json()

    @staticmethod
    def fromDB(product: ProductModel):
        return BestBuy(product.url)

    def toDB(self) -> ProductModel:
        return ProductModel(
            sku=self.sku,
            url=self.url,
            name=self.title,
            image_url=self.json["thumbnailImage"],
        )

    @property
    def title(self) -> str:
        return self.json["name"]

    @property
    def currentPrice(self) -> float:
        return float(self.json["salePrice"])

    @property
    def regularPrice(self) -> float:
        return float(self.json["regularPrice"])

    @property
    def isAvailable(self) -> bool:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        }
        res = requests.get(
            f"https://www.bestbuy.ca/ecomm-api/availability/products?skus={self.sku}",
            headers=headers,
        )
        if not (res.ok):
            raise error.BadRequestException(
                f"Could not retrieve availability, {res.reason} ({res.status_code})"
            )

        purchasable = json.loads(res.text.encode().decode("utf-8-sig"))[
            "availabilities"
        ][0]["shipping"]["purchasable"]
        return purchasable


class BestBuyCheckOut:
    def __init__(self, postal, region, item: BestBuy):
        self.session = requests.Session()
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        self.session.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "User-Agent": self.ua,
        }
        self.basketID = None
        self.basket = None
        self.postal = postal
        self.region = region
        self.item = item
        self.token = None
        self.dtpc = None

    def atc(self, quantity) -> str:
        sku = self.item.sku
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-CA",
            "cache-control": "no-cache",
            "Content-Type": "application/json",
            "dnt": "1",
            "Origin": "https://www.bestbuy.ca",
            "Postal-Code": self.postal,
            "Pragma": "no-cache",
            "Referer": self.item.url,
            "Region-Code": self.region,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": self.ua,
        }

        data = {"lineItems": [{"sku": str(sku), "quantity": int(quantity)}]}
        if self.basketID is not None:
            data.update({"id", self.basketID})

        res = self.session.post(
            "https://www.bestbuy.ca/api/basket/v2/baskets",
            headers=headers,
            data=json.dumps(data),
        )

        if not res.ok:
            # raise error.InternalServerException("Could not add item to cart.")
            raise error.IncorrectInfoException(res.reason)

        # print("ATC cookies: " + str(self.session.cookies.get_dict()))
        self.basketID = res.json()["id"]
        return self.basketID

    def getToken(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "dnt": "1",
            "Pragma": "no-cache",
            "Referer": "https://www.bestbuy.ca/en-ca/basket",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "User-Agent": self.ua,
        }
        payload = {
            "redirectUrl": "https://www.bestbuy.ca/checkout/?qit=1#/en-ca/shipping/ON/L8J",
            "lang": "en-CA",
            "contextId": "checkout",
        }

        res = self.session.get(
            "https://www.bestbuy.ca/identity/global/signin",
            headers=headers,
            params=payload,
        )

        if not res.ok:
            raise error.InternalServerException(res.reason)

        # print("Token cookies: " + str(self.session.cookies.get_dict()))
        tx = self.session.cookies.get("tx")
        self.token = tx
        return tx

    def getBasket(self):
        if self.basketID is None:
            raise error.IncorrectInfoException

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-ca",
            "cache-control": "no-cache",
            "Content-Type": "application/json",
            "dnt": "1",
            "Postal-Code": "L8J0K4",
            "Pragma": "no-cache",
            "Referer": "https://www.bestbuy.ca/checkout/?qit=1",
            "Region-Code": self.region,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": self.ua,
            "x-dtreferer": f"https://www.bestbuy.ca/checkout/?qit=1#/en-ca/shipping/{self.region}/{self.postal}",
        }

        res = self.session.get(
            f"https://www.bestbuy.ca/api/basket/v2/baskets/{self.basketID}",
            headers=headers,
        )
        self.basket = res.json()

        # print("Basket cookies: " + str(self.session.cookies.get_dict()))
        self.dtpc = self.session.cookies.get("dtpc")
        return res.json()

    def startCheckout(self):
        if self.basket is None or self.token is None:
            raise error.IncorrectInfoException

        headers = {
            "Accept": "application/vnd.bestbuy.checkout+json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-ca",
            "cache-control": "no-cache",
            "Content-Type": "application/json",
            "dnt": "1",
            "origin": "https://www.bestbuy.ca",
            "Pragma": "no-cache",
            "Referer": "https://www.bestbuy.ca/checkout/?qit=1",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": self.ua,
            "x-dtreferer": f"https://www.bestbuy.ca/checkout/?qit=1#/en-ca/shipping/{self.region}/{self.postal}",
            "x-tx": self.token,
        }

        lineItem = self.basket["shipments"][0]["lineItems"]
        seller = self.basket["shipments"][0]["seller"]

        itemToAdd = []
        for i in lineItem:
            dict = {
                "lintItemType": i["lineItemType"],
                "name": i["sku"]["product"]["name"],
                "offerId": i["sku"]["offer"]["id"],
                "quantity": i["quantity"],
                "sellerId": seller["id"],
                "sku": i["sku"]["id"],
                "total": i["totalPurchasePrice"],
            }
            itemToAdd.append(dict)

        data = {
            "email": "anthonyma940603@gmail.com",
            "lineItems": itemToAdd,
            "shippingAddress": {
                "address": "6-23 Echovalley Drive",
                "apartmentNumber": "",
                "city": "Stoney Creek",
                "country": "CA",
                "firstName": "Anthony",
                "lastName": "Ma",
                "phones": [{"ext": "", "phone": "2893211931"}],
                "postalCode": "L8J0K4",
                "province": "ON",
            },
        }

        res = self.session.post(
            "https://www.bestbuy.ca/api/checkout/checkout/orders",
            headers=headers,
            data=json.dumps(data),
        )

        # print("Checkout cookies: " + str(self.session.cookies.get_dict()))

        return res.json()
