import regex, json, requests, random
import webscraper.utility.errors as error
from typing import Dict
from webscraper.models.website import Website
from webscraper.models.products import ProductModel
from webscraper.models.profiles import ShoppingProfile
from webscraper.utility.config import BEST_BUY
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from base64 import b64encode


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

        x = json.loads(res.text.encode().decode("utf-8-sig"))["availabilities"][0][
            "shipping"
        ]

        purchasable = x["purchasable"] and x["status"] == "InStock"
        return purchasable


class BestBuyCheckOut:
    def __init__(self, profile: ShoppingProfile, item: BestBuy):
        self.session = requests.Session()
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
        try:
            with open("user-agents.json", "r") as f:
                x = json.load(f)
                self.ua = random.randint(0, len(x) - 1)
        except:
            pass

        self.profile = profile
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
        self.postal = self.profile.postalCode[:3]
        self.region = self.profile.province
        self.item = item
        self.token = None
        self.dtpc = None
        self.orderID = None
        self.order = None
        self.config = self.getConfig()

    def checkout(self):
        pass

    def getConfig(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "dnt": "1",
            "pragma": "no-cache",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "User-Agent": self.ua,
        }

        res = requests.get("https://www.bestbuy.ca/ch/config.json", headers=headers)
        self.config = res.json()
        return res.json()

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
            "Postal-Code": self.profile.postalCode.replace(" ", ""),
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
            "email": self.profile.email,
            "lineItems": itemToAdd,
            "shippingAddress": {
                "address": self.profile.address,
                "apartmentNumber": str(self.profile.apartmentNumber)
                if self.profile.apartmentNumber is not None
                else "",
                "city": self.profile.city,
                "country": self.profile.country,
                "firstName": self.profile.firstName,
                "lastName": self.profile.lastName,
                "phones": [
                    {
                        "ext": str(self.profile.extension)
                        if self.profile.extension is not None
                        else "",
                        "phone": str(self.profile.phoneNumber),
                    }
                ],
                "postalCode": self.profile.postalCode,
                "province": self.profile.province,
            },
        }

        res = self.session.post(
            "https://www.bestbuy.ca/api/checkout/checkout/orders",
            headers=headers,
            data=json.dumps(data),
        )

        # print("Checkout cookies: " + str(self.session.cookies.get_dict()))

        id = res.json()["id"]
        self.orderID = id
        return id

    def startPayment(self):
        if self.orderID is None:
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
            "x-dtreferer": f"https://www.bestbuy.ca/checkout/?qit=1#/en-ca/payment",
            "x-tx": self.token,
        }

        terminal = self.config["encryption"]["terminalNo"]
        public_key = self.config["encryption"]["publicKey"]
        if "BEGIN PUBLIC KEY" not in public_key:
            public_key = (
                f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
            )

        message = (str(terminal) + str(self.profile.creditCardNumber)).encode("utf-8")
        key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(key)
        encryptedCard = (
            b64encode(cipher.encrypt(message)).decode("utf-8")
            + str(self.profile.creditCardNumber)[-4:]
        )

        data = {
            "email": self.profile.email,
            "payment": {
                "creditCard": {
                    "billingAddress": {
                        "address": self.profile.address,
                        "apartmentNumber": str(self.profile.apartmentNumber)
                        if self.profile.apartmentNumber is not None
                        else "",
                        "city": self.profile.city,
                        "country": self.profile.country,
                        "firstName": self.profile.firstName,
                        "lastName": self.profile.lastName,
                        "phones": [
                            {
                                "ext": str(self.profile.extension)
                                if self.profile.extension is not None
                                else "",
                                "phone": str(self.profile.phoneNumber),
                            }
                        ],
                        "postalCode": self.profile.postalCode,
                        "province": self.profile.province,
                    },
                    "cardNumber": encryptedCard,
                    "cardType": "VISA",
                    "cvv": str(self.profile.cvv),
                    "expirationMonth": str(self.profile.expMonth),
                    "expirationYear": str(self.profile.expYear),
                }
            },
        }

        res = self.session.put(
            f"https://www.bestbuy.ca/api/checkout/checkout/orders/{self.orderID}/payments",
            headers=headers,
            data=json.dumps(data),
        )

        self.order = res.json()
        return res.json()

    def submitOrder(self):
        if self.orderID is None or self.order is None:
            raise error.IncorrectInfoException

        if (
            self.order["paymentMethodSummary"]["creditCardSummary"][
                "secureAccountRegistration"
            ]
            is not None
        ):
            # 3dsecure
            pass

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
            "x-dtreferer": f"https://www.bestbuy.ca/checkout/?qit=1#/en-ca/payment",
            "x-tx": self.token,
        }

        data = {
            "cvv": str(self.profile.cvv),
            "email": self.profile.email,
            "id": self.order["id"],
            "totalPurchasePrice": self.order["totalPurchasePrice"],
        }

        res = self.session.post(
            "https://www.bestbuy.ca/api/checkout/checkout/orders/submit",
            headers=headers,
            data=json.dumps(data),
        )

        return res.json()
