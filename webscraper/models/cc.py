from base64 import b64decode
from webscraper.utility.utils import CANADACOMPUTERS, getUA
from webscraper.models.website import Website
from webscraper.models.products import ProductModel
from webscraper.models.profiles import ShoppingProfile
from bs4 import BeautifulSoup
import webscraper.utility.errors as error
import regex, requests, json, random, datetime


class CanadaComputers(Website):
    def __init__(self, url):
        if not (
            match := regex.match(
                r"^https:\/\/www\.canadacomputers\.com\/product_info\.php\?.*item_id=(\d{6})",
                url,
            )
        ):
            raise error.IncorrectInfoException

        url = regex.sub(r"&sid=.*$", "", url)

        super().__init__(url=url, attributes=CANADACOMPUTERS, sku=int(match.group(1)))

    @property
    def name(self):
        return super().getName().get_text().strip()

    def getCurrentPrice(self) -> float:
        self.webObj = super().generateWebObj()
        price = super().getCurrentPrice().get_text().strip()
        return float(price[1:])

    def getRegularPrice(self) -> float:
        self.webObj = super().generateWebObj()
        price = super().getRegularPrice()

        if price:
            price = float(price.get_text().replace("Was:", "").strip()[1:])
        return price

    def getAvailability(self) -> bool:
        self.webObj = super().generateWebObj()
        return super().getAvailability() is not None

    @property
    def imageURL(self) -> str:
        return super().getImage().get("src")

    @staticmethod
    def fromDB(product: ProductModel):
        return CanadaComputers(product.url)

    def toDB(self) -> ProductModel:
        return ProductModel(
            sku=self.sku, url=self.url, name=self.name, image_url=self.imageURL
        )


class CanadaComputersCheckout:
    def __init__(self, profile: ShoppingProfile, item: CanadaComputers):
        self.session = requests.Session()
        self.ua = getUA()
        self.profile = profile
        self.item = item
        self.sid = None

        if not (self.profile.actEmail or self.profile.actPassword):
            raise Exception("Must provide CC account info.")

    def reset(self):
        self.sid = None

    def checkout(self):
        res = self.login()
        if not res:
            return

        res = self.deleteCart()
        if not res:
            return

        res = self.atc()
        if not res:
            return

        res = self.shipping()
        if not res:
            return

        res = self.delivery()
        if not res:
            return

        res = self.payment()
        if not res:
            return

        res = self.review()
        if not res:
            return

        res = self.moneris()
        if not res:
            return

        res = self.success()
        if not res:
            return

        if not self.order_id:
            return

        return self.order_id

    def getSID(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        res = self.session.get(self.item.url, headers=headers)
        if not res.ok:
            raise Exception(f"Could not retrieve SID, {res.reason}")

        self.sid = self.session.cookies.get("sid")
        return self.sid

    def login(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        data = {
            "lo-username": self.profile.actEmail,
            "lo-password": self.profile.actPassword,
            "login": "",
        }

        res = self.session.post(
            "https://www.canadacomputers.com/login.php",
            headers=headers,
            data=data,
        )
        if not res.ok:
            raise Exception(f"Could not log in, {res.reason}")

        return res

    def atc(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Pragma": "no-cache",
            "Referer": "https://www.canadacomputers.com",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        query = {
            "action": "bundle_add_to_cart",
            "item0": str(self.item.sku),
            "qty0": "1",
        }

        res = self.session.get(
            f"https://www.canadacomputers.com/shopping_cart.php",
            headers=headers,
            params=query,
        )

        if not res.ok:
            raise Exception(f"Could not add item to cart, {res.reason}")

        return res

    def getCart(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Pragma": "no-cache",
            "Referer": "https://www.canadacomputers.com/account.php",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        res = self.session.get(
            "https://www.canadacomputers.com/shopping_cart.php",
            headers=headers,
        )

        # return res

        soup = BeautifulSoup(res.text, "html.parser")

        form: BeautifulSoup = soup.find(name="form", id="shopping_cart")

        if not form:
            raise Exception("Could not retrieve cart, most likely due to atc error.")

        divs = form.find_all(name="div", attrs={"class": "py-4"})
        if not divs or len(divs) == 0:
            return None

        items = []

        for i in divs:
            qty = i.find(name="input", attrs={"name": "cart_quantity[]"})["value"]
            id = i.find(name="input", attrs={"name": "item_id[]"})["value"]
            items.append({"id": id, "qty": qty})

        return items

    def deleteCart(self):
        cart = self.getCart()
        if not cart:
            return

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Pragma": "no-cache",
            "Referer": "https://www.canadacomputers.com/shopping_cart.php",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        data = {
            "cart_quantity[]": [],
            "quantity[]": [],
            "item_id[]": [],
            "cart_delete[]": [],
        }

        for i in cart:
            data["cart_quantity[]"].append(i["qty"])
            data["quantity[]"].append(0)
            data["item_id[]"].append(str(i["id"]))
            data["cart_delete[]"].append(str(i["id"]))

        params = {"action": "update_product"}

        res = self.session.post(
            "https://www.canadacomputers.com/shopping_cart.php",
            headers=headers,
            data=data,
            params=params,
        )

        if not res.ok:
            raise Exception(f"Coult not empty existing cart, {res.reason}")

        return res

    def shipping(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Pragma": "no-cache",
            "Referer": "https://www.canadacomputers.com/shopping_cart.php",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        data = {
            "ch-method": "dropship",
            "ch-shiptoanother-firstname": self.profile.shippingAddress.firstName,
            "ch-shiptoanother-lastname": self.profile.shippingAddress.lastName,
            "ch-shiptoanother-company": "",
            "ch-shiptoanother-address": "",
            "ch-shiptoanother-suburb": "",
            "ch-shiptoanother-city": "",
            "ch-shiptoanother-prov-drpdn": "",
            "ch-shiptoanother-country": "Canada",
            "ch-shiptoanother-postal": "",
            "checkout_shipping": "",
        }

        # methodStart = time.perf_counter()
        # res = self.session.get(
        #     "https://www.canadacomputers.com/checkout_method.php", headers=headers
        # )
        # methodTotal = time.perf_counter() - methodStart
        # print(f"Method get time: {methodTotal}s")

        # shippingStart = time.perf_counter()
        res = self.session.get(
            "https://www.canadacomputers.com/checkout_shipping.php", headers=headers
        )
        # shippingTotal = time.perf_counter() - shippingStart
        # print(f"Shipping get time: {shippingTotal}s")

        if not res.ok:
            raise Exception(f"Could not retrieve cart, {res.reason}")

        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://www.canadacomputers.com"
        headers["Referer"] = "https://www.canadacomputers.com/?checkout-shipping"

        # print(self.session.cookies.get_dict())
        # postStart = time.perf_counter()
        res = self.session.post(
            "https://www.canadacomputers.com/checkout_shipping.php",
            headers=headers,
            data=data,
        )
        # postTotal = time.perf_counter() - postStart
        # print(f"POST time: {postTotal}s")

        if not res.ok:
            raise Exception(f"Could not POST to shipping page, {res.reason}")
        # return res

        soup = BeautifulSoup(res.text, "html.parser")

        form = soup.find(name="form", attrs={"name": "checkout_shipping_option"})

        if not form:
            raise Exception(
                f"Could not find any shipping options, most likely due to atc problems."
            )

        divs = form.find_all(name="div", attrs={"id": regex.compile(r"^row\_\d$")})

        if not divs:
            raise Exception(
                f"Could not find any shipping options, most likely due to atc problems."
            )

        options = list(
            map(
                lambda i: {
                    "name": divs[i].find(name="input", id=f"shipname_{i}")["value"],
                    "price": divs[i].find(name="input", id=f"shipprice_{i}")["value"],
                    "date": divs[i].find(name="input", id=f"shipdate_{i}")["value"],
                    "courier": divs[i].find(name="input", id=f"courier_{i}")["value"],
                    "insurance_type": "ins_free",
                    "insurance_amt": "0",
                },
                divs,
            )
        )
        # for i in range(len(divs)):
        #     options.append(
        #         {
        #             "name": divs[i].find(name="input", id=f"shipname_{i}")["value"],
        #             "price": divs[i].find(name="input", id=f"shipprice_{i}")["value"],
        #             "date": divs[i].find(name="input", id=f"shipdate_{i}")["value"],
        #             "courier": divs[i].find(name="input", id=f"courier_{i}")["value"],
        #             "insurance_type": "ins_free",
        #             "insurance_amt": "0",
        #         }
        #     )

        if len(options) < 1:
            raise Exception("Could not retrieve shipping options")

        ship = 0
        if len(options) > 1:
            for i in range(1, len(options)):
                if float(options[i]["price"]) < float(options[ship]["price"]):
                    ship = i
                    continue
                if float(options[i]["price"]) == float(options[ship]["price"]):
                    shipDate = None
                    iDate = None
                    try:
                        shipDate = datetime.datetime.strptime(
                            options[ship]["date"], "%Y-%m-%d"
                        ).date()
                    except:
                        pass
                    try:
                        iDate = datetime.datetime.strptime(
                            options[i]["date"], "%Y-%m-%d"
                        ).date()
                    except:
                        pass

                    if shipDate is not None and iDate is not None:
                        if iDate < shipDate:
                            ship = i
                            continue
                    elif shipDate is None or iDate is None:
                        if iDate is not None:
                            ship = i
                            continue

        self.shipping_data = {
            "ship": ship,
            "shipname": options[ship]["name"],
            "shipprice": options[ship]["price"],
            "shipdate": options[ship]["date"],
            "courier": options[ship]["courier"],
            "insurance": options[ship]["insurance_type"],
            "insurance_type": options[ship]["insurance_type"],
            "insurance_amt": options[ship]["insurance_amt"],
            "checkout_shipping_option": "",
        }

        return res

    def delivery(self):
        if not self.shipping_data:
            raise Exception("Missing shipping data")
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Origin": "https://www.canadacomputers.com",
            "Pragma": "no-cache",
            "Referer": "https://www.canadacomputers.com/checkout_shipping_option.php",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        res = self.session.post(
            "https://www.canadacomputers.com/checkout_shipping_option.php",
            headers=headers,
            data=self.shipping_data,
        )

        if not res.ok:
            raise Exception(f"Could not submit shipping options, {res.reason}")

        return res

    def payment(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Origin": "https://www.canadacomputers.com",
            "Pragma": "no-cache",
            "Referer": "https://www.canadacomputers.com/?checkout-shipping-option",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        data = {
            "ch-methodofpayment": "credit_card",
            "ch-frm-flexiticard-number": "",
            "checkout_payment": "",
        }

        res = self.session.post(
            "https://www.canadacomputers.com/checkout_payment.php",
            headers=headers,
            data=data,
        )

        if not res.ok:
            raise Exception(f"Could not submit payment options, {res.reason}")

        return res

    def review(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Origin": "https://www.canadacomputers.com",
            "Pragma": "no-cache",
            "Referer": "https://www.canadacomputers.com/?checkout-confirmation",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        data = {"ch_shippingtnc": "agree", "checkout_confirmation": ""}

        res = self.session.post(
            "https://www.canadacomputers.com/checkout_confirmation.php",
            headers=headers,
            data=data,
        )

        if not res.ok:
            raise Exception(f"Could not submit review, {res.reason}")

        soup = BeautifulSoup(res.text, "html.parser")

        def getValue(name):
            x = soup.find(attrs={"name": name})
            return x.get("value") or ""

        self.confirmation_data = {
            "ps_store_id": getValue("ps_store_id"),
            "hpp_key": getValue("hpp_key"),
            "charge_total": getValue("charge_total"),
            "shipping_cost": getValue("shipping_cost"),
            "cust_id": getValue("cust_id"),
            "order_id": getValue("order_id"),
            "lang": getValue("lang"),
            "email": getValue("email"),
            "note": getValue("note"),
            "hst": getValue("hst"),
            "id1": getValue("id1"),
            "description1": getValue("description1"),
            "quantity1": getValue("quantity1"),
            "price1": getValue("price1"),
            "subtotal1": getValue("subtotal1"),
            "ship_first_name": getValue("ship_first_name"),
            "ship_last_name": getValue("ship_last_name"),
            "ship_company_name": getValue("ship_company_name"),
            "ship_address_one": getValue("ship_address_one"),
            "ship_city": getValue("ship_city"),
            "ship_state_or_province": getValue("ship_state_or_province"),
            "ship_postal_code": getValue("ship_postal_code"),
            "ship_country": getValue("ship_country"),
            "bill_first_name": getValue("bill_first_name"),
            "bill_last_name": getValue("bill_last_name"),
            "bill_company_name": getValue("bill_company_name"),
            "bill_address_one": getValue("bill_address_one"),
            "bill_city": getValue("bill_city"),
            "bill_state_or_province": getValue("bill_state_or_province"),
            "bill_postal_code": getValue("bill_postal_code"),
            "bill_country": getValue("bill_country"),
            "bill_phone": getValue("bill_phone"),
        }

        return self.confirmation_data

    def moneris(self):
        if not self.confirmation_data:
            raise Exception("Missing confirmation data")

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,zh;q=0.8,zh-CN;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            "Host": "www3.moneris.com",
            "Origin": "https://www.canadacomputers.com",
            "Pragma": "no-cache",
            "Referer": "https://www.canadacomputers.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        res = self.session.post(
            "https://www3.moneris.com/HPPDP/index.php",
            headers=headers,
            data=self.confirmation_data,
        )

        if not res.ok:
            raise Exception(f"Could not submit moneris request, {res.reason}")

        # return res

        soup = BeautifulSoup(res.text, "html.parser")
        script = soup.find(
            name="script", attrs={"type": "text/javascript", "src": None}
        )

        match = regex.search(
            r"""var\s*post_data\s*=\s*"hpp_id=([\w]+)"\s*\+\s*"&hpp_ticket=([\w]+)""",
            script.string,
        )

        hpp_id = match.group(1)
        hpp_ticket = match.group(2)

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "DNT": "1",
            "Host": "www3.moneris.com",
            "Origin": "https://www3.moneris.com",
            "Pragma": "no-cache",
            "Referer": "https://www3.moneris.com/HPPDP/index.php",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": self.ua,
        }

        data = {
            "hpp_id": hpp_id,
            "hpp_ticket": hpp_ticket,
            "pan": self.profile.creditCard.creditCardNumber,
            "pan_mm": self.profile.creditCard.twoDigitExpMonth,
            "pan_yy": self.profile.creditCard.twoDigitExpYear,
            "pan_cvd": self.profile.creditCard.cvv,
            "cardholder": self.profile.creditCard.fullName,
            "avs_str_num": self.profile.creditCard.billingAddress.streetNumber,
            "avs_str_name": self.profile.creditCard.billingAddress.streetName,
            "avs_zip_code": self.profile.creditCard.billingAddress.postalCode,
            "avs_po_box_addr": "",
            "doTransaction": "cc_purchase",
        }

        res = self.session.post(
            "https://www3.moneris.com/HPPDP/hprequest.php", headers=headers, data=data
        )

        if not res.ok:
            raise Exception("POST to HPRequest.php failed.")

        monerisResult = res.json()

        if (
            monerisResult["response"]["error"] != ""
            or monerisResult["response"]["data"]["form"] == ""
        ):
            raise Exception(400)

        html = b64decode(monerisResult["response"]["data"]["form"])

        soup = BeautifulSoup(str(html), "html.parser")

        form = soup.find(name="form", attrs={"name": "downloadForm"})

        if not form:
            raise Exception("Moneris HPRequest.php failed.")
        url = form.get("action").strip()

        data = {}

        inputs = soup.find_all(name="input", attrs={"type": "hidden"})

        for input in inputs:
            data[input["name"]] = input["value"]

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www3.moneris.com",
            "referer": "https://www3.moneris.com/HPPDP/hprequest.php",
            "upgrade-insecure-requests": "1",
            "user-agent": self.ua,
        }

        res = self.session.post(url, data=data, headers=headers)

        if not res.ok:
            raise Exception("POST to 3dsecure failed.")

        headers["origin"] = "https://authentication.cardinalcommerce.com"
        headers["referer"] = res.url

        soup = BeautifulSoup(res.text, "html.parser")

        form = soup.find(name="form", attrs={"id": "TermForm"})
        url = form.get("action").strip()
        pares = form.find(name="input", attrs={"name": "PaRes"}).get("value")
        md = form.find(name="input", attrs={"name": "MD"}).get("value")

        match = regex.search(
            r"xid=(\w+)&(?:amp;)?hppdp_id=(\w+)&(?:amp;)?ticket=(\w+)", md
        )

        xid = match.group(1)
        hpp_id = match.group(2)
        hpp_ticket = match.group(3)

        data = {
            "hpp_id": hpp_id,
            "hpp_ticket": hpp_ticket,
            "PaRes": pares,
            "xid": xid,
            "doTransaction": "cc_purchase",
        }

        res = self.session.post(
            "https://www3.moneris.com/HPPDP/hprequest.php", data=data
        )

        if not res.ok:
            raise Exception("POST to hprequest after 3d secure failed.")

        html = b64decode(res.json()["response"]["data"]["form"])

        soup = BeautifulSoup(str(html), "html.parser")

        inputs = soup.find_all(name="input")

        success = {}

        for input in inputs:
            success[input["name"]] = input["value"]

        self.success_data = success

        return res

    def success(self):
        if not self.success_data:
            raise Exception("Missing success data.")
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "DNT": "1",
            "Host": "www.canadacomputers.com",
            "Origin": "https://www3.moneris.com",
            "Pragma": "no-cache",
            "Referer": "https://www3.moneris.com/HPPDP/index.php",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
        }

        data = self.success_data

        res = self.session.post(
            "https://www.canadacomputers.com/checkout_success.php",
            headers=headers,
            data=data,
        )

        if not res.ok:
            raise Exception(f"Could not post to success.php, {res.reason}")

        soup = BeautifulSoup(res.text, "html.parser")
        pattern = regex.compile(r"^Order Number: (\d+)$")
        order = soup.find(text=pattern)
        id = regex.search(pattern, order)
        self.order_id = id

        return res
