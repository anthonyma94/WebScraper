from bs4 import BeautifulSoup
import regex, json, requests, random

from requests.api import head
import webscraper.utility.errors as error
from typing import Dict
from webscraper.models.website import Website
from webscraper.models.products import ProductModel
from webscraper.models.profiles import ShoppingProfile
from webscraper.utility.utils import BEST_BUY, PROVINCES, getUA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from base64 import b64encode


class BestBuy(Website):
    def __init__(self, url):
        if not (
            match := regex.match(
                r"^https:\/\/www\.bestbuy\.ca\/en-ca\/product\/.*(\d{8}).*$", url
            )
        ):
            raise error.IncorrectInfoException("Incorrect URL.")

        url = regex.sub(r"(?<=\d{8}).*$", "", url)

        super().__init__(url, BEST_BUY, sku=int(match.group(1)), webObj=False)

        self.json = self.getJSON()

        self.headers = {
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
            "User-Agent": getUA(),
        }

    def getJSON(self) -> Dict:
        url = f"https://www.bestbuy.ca/api/v2/json/product/{self.sku}"
        res = requests.get(url, headers=self.headers)
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
            name=self.name,
            image_url=self.json["thumbnailImage"],
        )

    @property
    def name(self) -> str:
        return self.json["name"]

    def getCurrentPrice(self) -> float:
        return float(self.getJSON()["salePrice"])

    def getRegularPrice(self) -> float:
        return float(self.getJSON()["regularPrice"])

    def getAvailability(self) -> bool:
        # headers = {"User-Agent": getUA()}
        res = requests.get(
            f"https://www.bestbuy.ca/ecomm-api/availability/products?skus={self.sku}",
            headers=self.headers,
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
        self.ua = getUA()

        self.profile = profile
        self.basketID = None
        self.basket = None
        self.postal = self.profile.shippingAddress.postalCode[:3]
        self.region = self.profile.shippingAddress.province
        self.item = item
        self.token = None
        self.dtpc = None
        self.orderID = None
        self.order = None
        self.config = self.getConfig()

    def reset(self):
        self.session = requests.Session()
        self.basketID = None
        self.basket = None
        self.token = None
        self.dtpc = None
        self.orderID = None
        self.order = None

    def checkout(self):
        print("Adding to cart...")
        basketID = self.atc()
        if not basketID:
            raise Exception("Could not add to cart.")

        print(f"Basket ID: {basketID}. Retrieving token...")
        res = self.getToken()
        if not res:
            raise Exception("Could not retrieve CSRF token.")

        print("Token retrieved. Retrieving basket...")
        res = self.getBasket()
        if not res:
            raise Exception("Could not retrieve basket.")

        print("Basket retrieved. Starting checkout...")
        res = self.startCheckout()
        if not res:
            raise Exception("Could not start checkout.")

        print("Starting payment...")
        res = self.startPayment()
        if not res:
            raise Exception("Could not start payment.")

        # cookies, res = self.submitOrder()
        # return cookies, res

        print("Submitting order...")
        orderNumber = self.submitOrder()
        if not orderNumber:
            raise Exception("Could not submit order.")

        return orderNumber

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

        if not res.ok:
            raise Exception("Could not retrieve config.json.")

        self.config = res.json()
        return res.json()

    def atc(self) -> str:
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

        data = {"lineItems": [{"sku": str(sku), "quantity": 1}]}
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
            "redirectUrl": f"https://www.bestbuy.ca/checkout/?qit=1#/en-ca/shipping/ON/{self.postal}",
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

        tx = self.session.cookies.get("tx")

        if not tx:
            raise error.InternalServerException

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
            "Postal-Code": self.profile.shippingAddress.postalCode.replace(" ", ""),
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

        if not res.ok:
            raise Exception("Could not retrieve basket.")

        self.basket = res.json()

        # self.dtpc = self.session.cookies.get("dtpc")
        # if not self.dtpc:
        #     raise Exception("Could not retrieve dtpc token.")

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
                "address": self.profile.shippingAddress.address,
                "apartmentNumber": str(self.profile.shippingAddress.apartmentNumber)
                if self.profile.shippingAddress.apartmentNumber is not None
                else "",
                "city": self.profile.shippingAddress.city,
                "country": self.profile.shippingAddress.country,
                "firstName": self.profile.shippingAddress.firstName,
                "lastName": self.profile.shippingAddress.lastName,
                "phones": [
                    {
                        "ext": str(self.profile.shippingAddress.extension)
                        if self.profile.shippingAddress.extension is not None
                        else "",
                        "phone": str(self.profile.shippingAddress.phoneNumber),
                    }
                ],
                "postalCode": self.profile.shippingAddress.postalCode.replace(" ", ""),
                "province": self.profile.shippingAddress.province
                if len(self.profile.shippingAddress.province) == 2
                else PROVINCES[str(self.profile.shippingAddress.province).title()],
            },
        }

        res = self.session.post(
            "https://www.bestbuy.ca/api/checkout/checkout/orders",
            headers=headers,
            data=json.dumps(data),
        )

        if not res.ok:
            raise Exception(f"POST orders failed, {res.reason}")

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

        message = (
            str(terminal) + str(self.profile.creditCard.creditCardNumber)
        ).encode("utf-8")
        key = RSA.import_key(public_key)
        cipher = PKCS1_OAEP.new(key)
        encryptedCard = b64encode(cipher.encrypt(message)).decode("utf-8") + str(
            self.profile.creditCard.lastFour
        )

        data = {
            "email": self.profile.email,
            "payment": {
                "creditCard": {
                    "billingAddress": {
                        "address": self.profile.creditCard.billingAddress.address,
                        "apartmentNumber": str(
                            self.profile.creditCard.billingAddress.apartmentNumber
                        )
                        if self.profile.creditCard.billingAddress.apartmentNumber
                        is not None
                        else "",
                        "city": self.profile.creditCard.billingAddress.city,
                        "country": "CA",
                        "firstName": self.profile.creditCard.billingAddress.firstName,
                        "lastName": self.profile.creditCard.billingAddress.lastName,
                        "phones": [
                            {
                                "ext": str(
                                    self.profile.creditCard.billingAddress.extension
                                )
                                if self.profile.creditCard.billingAddress.extension
                                is not None
                                else "",
                                "phone": str(
                                    self.profile.creditCard.billingAddress.phoneNumber
                                ),
                            }
                        ],
                        "postalCode": self.profile.creditCard.billingAddress.postalCode.replace(
                            " ", ""
                        ),
                        "province": self.profile.creditCard.billingAddress.province
                        if len(self.profile.creditCard.billingAddress.province) == 2
                        else PROVINCES[
                            str(self.profile.creditCard.billingAddress.province).title()
                        ],
                    },
                    "cardNumber": encryptedCard,
                    "cardType": str(self.profile.creditCard.type).upper(),
                    "cvv": str(self.profile.creditCard.cvv),
                    "expirationMonth": str(self.profile.creditCard.expMonth),
                    "expirationYear": str(self.profile.creditCard.expYear),
                }
            },
        }

        res = self.session.put(
            f"https://www.bestbuy.ca/api/checkout/checkout/orders/{self.orderID}/payments",
            headers=headers,
            data=json.dumps(data),
        )

        if not res.ok:
            raise Exception(f"Payment failed, {res.reason}")

        self.order = res.json()
        return res.json()

    def submitOrder(self):
        if self.orderID is None or self.order is None:
            raise error.IncorrectInfoException

        pares = ""
        if (
            self.order["paymentMethodSummary"]["creditCardSummary"][
                "secureAccountRegistration"
            ]
            is not None
        ):
            pares = self.handle_3dsecure()
            # 3dsecure
            # cookies, res = self.handle_3dsecure()
            # return cookies, res

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
            "cvv": str(self.profile.creditCard.cvv),
            "email": self.profile.email,
            "id": self.order["id"],
            "totalPurchasePrice": self.order["totalPurchasePrice"],
        }

        if pares:
            data["secureAuthenticationResponse"] = pares

        res = self.session.post(
            "https://www.bestbuy.ca/api/checkout/checkout/orders/submit",
            headers=headers,
            data=json.dumps(data),
        )

        if not res.ok:
            raise Exception(f"Could not submit order, {res.reason}")

        with open("bestbuy-order-success.html", "wb") as f:
            f.write(res.content)

        self.session.delete(
            f"https://www.bestbuy.ca/api/basket/v2/baskets/{self.basketID}",
            headers=headers,
        )

        return res.json()["orderNumber"]

    def handle_3dsecure(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "dnt": "1",
            "host": "0eaf.cardinalcommerce.com",
            "origin": "https://www.bestbuy.ca",
            "Pragma": "no-cache",
            "Referer": "https://www.bestbuy.ca/",
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-fetch-user": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        resp = self.order["paymentMethodSummary"]["creditCardSummary"][
            "secureAccountRegistration"
        ]

        url = resp["bankUrl"]
        data = {
            "PaReq": resp["bankParameters"],
            "MD": resp["orderId"],
            "TermUrl": resp["termUrl"],
        }

        res = self.session.post(url, headers=headers, data=data)

        if not res.ok:
            raise Exception(f"3D Secure redirection failed, {res.reason}")

        soup = BeautifulSoup(res.content, "html.parser")

        form = soup.find(name="form", attrs={"method": "POST"})

        if not form:
            with open("1-redirect-staging.html", "wb") as f:
                f.write(res.content)
            raise Exception("3D Secure 1-redirect.html failed.")

        url = form["action"]
        inputs = form.find_all(name="input", attrs={"type": "hidden"})

        data = {}
        for i in inputs:
            name = i["name"]
            value = i["value"]
            data[name] = value

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "dnt": "1",
            "host": "authentication.cardinalcommerce.com",
            "origin": "https://0eaf.cardinalcommerce.com",
            "Pragma": "no-cache",
            "Referer": "https://0eaf.cardinalcommerce.com/",
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        }

        res = self.session.post(url, headers=headers, data=data)

        if not res.ok:
            raise Exception("3D-Secure failed.")

        soup = BeautifulSoup(res.content, "html.parser")

        form = soup.find(name="form", attrs={"id": "TermForm"})

        if not form:
            with open("2-payer-authentication-staging.html", "wb") as f:
                f.write(res.content)
            raise Exception("3D Secure 2-payer-authentication.html failed.")

        if (url := form.get("action")) is None:
            res = self.handle_processing_risk(soup)
        else:
            inputs = form.find_all(name="input", attrs={"type": "hidden"})
            data = {}

            for i in inputs:
                data[i["name"]] = i["value"]

            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded",
                "dnt": "1",
                "host": "0eaf.cardinalcommerce.com",
                "origin": "https://authentication.cardinalcommerce.com",
                "Pragma": "no-cache",
                "Referer": "https://authentication.cardinalcommerce.com/",
                "sec-fetch-dest": "iframe",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-site",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
            }

            res = self.session.post(url, headers=headers, data=data)

        soup = BeautifulSoup(res.content, "html.parser")
        form = soup.find(name="form", attrs={"method": "post"})

        if not form:
            with open("3-term-staging.html", "wb") as f:
                f.write(res.content)
            raise Exception("3D Secure 3-term.html failed.")

        inputs = form.find_all(name="input", attrs={"type": "hidden"})

        data = {}
        pares = ""
        for i in inputs:
            if i["name"].lower() == "pares":
                pares = i["value"]
            data[i["name"]] = i["value"]

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "dnt": "1",
            "origin": "https://0eaf.cardinalcommerce.com",
            "Pragma": "no-cache",
            "Referer": "https://0eaf.cardinalcommerce.com/",
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        }

        res = self.session.post(
            "https://www.bestbuy.ca/api/checkout/payment/secureauth/bankresponse",
            headers=headers,
            data=data,
        )

        # return self.session.cookies.get_dict(), res
        return pares

    def handle_processing_risk(self, soup: BeautifulSoup):
        form = soup.find(name="form", attrs={"id": "ProcessRiskForm"})

        if not form:
            with open("2-payer-authentication-staging.html", "w") as f:
                f.write(soup.prettify())
            raise Exception("3D Secure 2-payer-authentication.html failed.")

        inputs = form.find_all(name="input", attrs={"type": "hidden"})
        data = {}
        transID = ""

        for i in inputs:
            data[i["name"]] = i["value"]
            if i["name"] == "TransactionId":
                transID = i["value"]

        data["X-Requested-With"] = "XMLHttpRequest"
        data["X-HTTP-Method-Override"] = "FORM"

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "dnt": "1",
            "host": "0eaf.cardinalcommerce.com",
            "origin": "https://authentication.cardinalcommerce.com",
            "Pragma": "no-cache",
            "Referer": "https://authentication.cardinalcommerce.com/",
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        }

        res = self.session.post(
            "https://authentication.cardinalcommerce.com/Api/NextStep/ProcessRisk",
            headers=headers,
            data=data,
        )

        if not res.ok:
            raise Exception("3dsecure failed.")

        # with open("3-ProcessRisk.html", "wb") as f:
        #     f.write(res.content)

        # exit(0)

        resp = res.json()

        data = {"TransactionId": transID, "IssuerId": resp["IssuerId"]}

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "dnt": "1",
            "host": "authentication.cardinalcommerce.com",
            "origin": "https://authentication.cardinalcommerce.com",
            "Pragma": "no-cache",
            "Referer": f"https://authentication.cardinalcommerce.com/ThreeDSecure/V1_0_2/PayerAuthentication?issuerId={data['IssuerId']}&transactionId={data['TransactionId']}",
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        }

        res = self.session.post(
            "https://authentication.cardinalcommerce.com/api/nextstep/term",
            headers=headers,
            data=data,
        )

        # with open("4-nextstep.html", "wb") as f:
        #     f.write(res.content)

        # exit(0)

        resp = res.json()

        data = {"PaRes": resp["Payload"]["PARes"], "MD": resp["Payload"]["MD"]}

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "dnt": "1",
            "host": "0eaf.cardinalcommerce.com",
            "origin": "https://authentication.cardinalcommerce.com",
            "Pragma": "no-cache",
            "Referer": "https://authentication.cardinalcommerce.com/",
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
        }

        res = self.session.post(
            "https://0eaf.cardinalcommerce.com/EAFService/jsp/v1/term",
            headers=headers,
            data=data,
        )

        # with open("5-term.html", "wb") as f:
        #     f.write(res.content)

        return res