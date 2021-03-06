import os
import regex, json
from webscraper.utility.utils import db, add_to_database
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from sqlalchemy import and_


class AddressModel(db.Model):
    __tablename__ = "addresses"
    __table_args__ = (
        db.UniqueConstraint("postal_code", "address", name="_uc_address"),
    )
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    apartment_number = db.Column(db.String)
    city = db.Column(db.String, nullable=False)
    province = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    postal_code = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    extension = db.Column(db.String)

    def __eq__(self, other):
        if isinstance(other, AddressModel):
            return (
                self.postal.replace(" ", "").upper()
                == other.postal.replace(" ", "").upper()
            ) and (self.address.upper() == other.address.upper())

        return False

    def __repr__(self):
        return self.toDict()

    def toDict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "apartment_number": self.apartment_number or "",
            "city": self.city,
            "province": self.province,
            "country": self.country,
            "postal_code": self.postal_code,
            "phone_number": self.phone_number,
            "extension": self.extension or "",
        }

    def add_to_database(self, **kwargs):
        return add_to_database(
            self,
            AddressModel.query.filter(
                and_(
                    AddressModel.postal_code == self.postal_code,
                    AddressModel.address == self.address,
                )
            ).first(),
            **kwargs,
        )


class CreditCardModel(db.Model):
    __tablename__ = "credit_card"
    __table_args__ = (
        db.UniqueConstraint("cvv", "exp_month", "exp_year", name="_uc_credit"),
    )

    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    cvv = db.Column(db.Integer, nullable=False)
    exp_month = db.Column(db.Integer, nullable=False)
    exp_year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    billing_address = db.Column(db.Integer, db.ForeignKey("addresses.id"))
    shopping_profile = db.relationship("ProfileModel", backref="credit_card", lazy=True)

    def __init__(self, **kwargs):
        super(CreditCardModel, self).__init__(**kwargs)

        if not (CreditCard.is_encrypted(self.card_number)):
            self.card_number = CreditCard.encrypt(self.card_number)

        if self.exp_year < 2000:
            self.exp_year += 2000

    def __repr__(self):
        return self.toDict()

    def toDict(self):
        billing = AddressModel.query.get(self.billing_address)
        card = CreditCard.decrypt(self.card_number)
        return {
            "id": self.id,
            "card_number": "*" * 12 + card[-4:],
            "first_name": self.first_name,
            "last_name": self.last_name,
            "cvv": self.cvv,
            "exp_month": self.exp_month,
            "exp_year": self.exp_year,
            "type": self.type,
            "billing_address": billing.toDict(),
        }

    def add_to_database(self, **kwargs):
        return add_to_database(
            self,
            CreditCardModel.query.filter(
                and_(
                    CreditCardModel.cvv == self.cvv,
                    CreditCardModel.exp_month == self.exp_month,
                    CreditCardModel.exp_year == self.exp_year,
                )
            ).first(),
            **kwargs,
        )


class ProfileModel(db.Model):
    __tablename__ = "profiles"
    __table_args__ = (
        db.UniqueConstraint("email", "shipping_address", "card", name="_uc"),
    )
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    shipping_address = db.Column(
        db.Integer, db.ForeignKey("addresses.id"), nullable=False
    )
    account = db.Column(db.String)
    card = db.Column(db.Integer, db.ForeignKey("credit_card.id"), nullable=False)

    def __repr__(self):
        return self.toDict()

    def toDict(self):
        shipping = AddressModel.query.get(self.shipping_address)
        return {
            "id": self.id,
            "email": self.email,
            "shipping_address": shipping.toDict(),
            "credit_card": (CreditCardModel.query.get(self.card)).toDict(),
            "account": json.loads(self.account) if self.account else None,
        }

    def add_to_database(self, **kwargs):
        return add_to_database(
            self,
            ProfileModel.query.filter(
                and_(
                    ProfileModel.email == self.email,
                    ProfileModel.shipping_address == self.shipping_address,
                    ProfileModel.card == self.card,
                )
            ).first(),
            **kwargs,
        )


class Address:
    def __init__(
        self,
        address,
        city,
        firstName,
        lastName,
        phoneNumber,
        postalCode,
        province,
        country="CA",
        apartmentNumber=None,
        extension=None,
        id=None,
    ):
        self.address = address
        self.apartmentNumber = apartmentNumber
        self.city = city
        self.country = country
        self.firstName = firstName
        self.lastName = lastName
        self.phoneNumber = phoneNumber
        self.extension = extension
        self.postalCode = postalCode
        self.province = province
        if id:
            self.id = id

    def __repr__(self):
        return str(self.__dict__)

    @property
    def streetNumber(self):
        return int(regex.search(r"^(?:\d+-)?(\d+)", self.address).group(1).strip())

    @property
    def streetName(self):
        return regex.search(r"\s([a-zA-Z0-9-\s]+)", self.address).group(1).strip()

    @staticmethod
    def fromDB(model: AddressModel):
        return Address(
            id=model.id,
            address=model.address,
            city=model.city,
            firstName=model.first_name,
            lastName=model.last_name,
            phoneNumber=model.phone_number,
            postalCode=model.postal_code,
            province=model.province,
            country=model.country,
            apartmentNumber=model.apartment_number,
            extension=model.extension,
        )

    def toDB(self):
        x = {
            "first_name": self.firstName,
            "last_name": self.lastName,
            "address": self.address,
            "apartment_number": self.apartmentNumber,
            "city": self.city,
            "province": self.province,
            "country": self.country,
            "postal_code": self.postalCode,
            "phone_number": self.phoneNumber,
            "extension": self.extension,
        }

        try:
            if self.id:
                x["id"] = self.id
        except AttributeError:
            pass
        return AddressModel(**x)


class CreditCard:
    @staticmethod
    def get_public_key():
        with open(f"{os.environ.get('DATA_URI') or '.'}/public.pem", "r") as f:
            key = f.read()
        return key

    def __init__(
        self,
        firstName: str,
        lastName: str,
        creditCardNumber,
        cvv: int,
        expMonth: int,
        expYear: int,
        type,
        billingAddress: Address,
        id: int = None,
    ):
        self.firstName = firstName
        self.lastName = lastName
        self.creditCardNumber = creditCardNumber
        self.cvv = int(cvv)
        self.expMonth = int(expMonth)
        self.expYear = int(expYear)
        self.type = type
        self.billingAddress = billingAddress
        if id:
            self.id = id

        if CreditCard.is_encrypted(self.creditCardNumber):
            self.creditCardNumber = CreditCard.decrypt(self.creditCardNumber)

        if int(self.expYear) < 2000:
            self.expYear = int(self.expYear) + 2000

    @property
    def fullName(self):
        return f"{self.firstName} {self.lastName}"

    @property
    def lastFour(self):
        return self.creditCardNumber[-4:]

    @property
    def twoDigitExpMonth(self):
        if int(self.expMonth) < 10:
            return f"0{str(self.expMonth)}"
        return str(self.expMonth)

    @property
    def twoDigitExpYear(self):
        year = int(self.expYear) - 2000
        if year < 10:
            return f"0{str(year)}"
        return str(year)

    @staticmethod
    def fromDB(model: CreditCardModel):
        address = AddressModel.query.get(model.billing_address)
        return CreditCard(
            id=model.id,
            firstName=model.first_name,
            lastName=model.last_name,
            creditCardNumber=CreditCard.decrypt(model.card_number),
            cvv=model.cvv,
            expMonth=model.exp_month,
            expYear=model.exp_year,
            type=model.type,
            billingAddress=Address.fromDB(address),
        )

    def toDB(self):
        address = self.billingAddress.toDB().add_to_database()
        x = {
            "card_number": CreditCard.encrypt(self.creditCardNumber),
            "first_name": self.firstName,
            "last_name": self.lastName,
            "cvv": self.cvv,
            "exp_month": self.expMonth,
            "exp_year": self.expYear,
            "type": self.type,
            "billing_address": address.id,
        }
        try:
            if self.id:
                x["id"] = self.id
        except AttributeError:
            pass

        return CreditCardModel(**x)

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def is_encrypted(message):
        return len(str(message)) > 16 or str(message)[-1] == "="

    @staticmethod
    def decrypt(ciphertext):
        ciphertext = b64decode(ciphertext.encode("utf-8"))
        with open(f"{os.environ.get('DATA_URI') or '.'}/private.pem", "r") as f:
            key = RSA.import_key(f.read())
        cipher = PKCS1_OAEP.new(key, SHA256)
        message = cipher.decrypt(ciphertext)
        return message.decode("utf-8")

    @staticmethod
    def encrypt(message) -> str:
        """Encrypts a given message using SHA-256

        Args:
            message (str): message to encrypt

        Returns:
            str: base64 encoded encrypted message
        """
        data = str(message).encode("utf-8")
        key = RSA.import_key(CreditCard.get_public_key())
        cipher = PKCS1_OAEP.new(key, SHA256)
        ciphertext = cipher.encrypt(data)
        return b64encode(ciphertext).decode("utf-8")


class ShoppingProfile:
    def __init__(
        self,
        email,
        shippingAddress: Address,
        creditCard: CreditCard,
        id=None,
        actEmail=None,
        actPassword=None,
    ):
        self.email = email
        self.shippingAddress = shippingAddress
        self.creditCard = creditCard
        if id:
            self.id = id
        if actEmail:
            self.actEmail = actEmail
        if actPassword:
            self.actPassword = actPassword

    @staticmethod
    def fromDB(model: ProfileModel):
        address = AddressModel.query.get(model.shipping_address)
        credit = CreditCardModel.query.get(model.card)
        return ShoppingProfile(
            id=model.id,
            email=model.email,
            shippingAddress=Address.fromDB(address),
            creditCard=CreditCard.fromDB(credit),
            actEmail=json.loads(model.account)["username"] if model.account else None,
            actPassword=json.loads(model.account)["password"]
            if model.account
            else None,
        )

    def toDB(self):
        address = self.shippingAddress.toDB().add_to_database()

        credit = self.creditCard.toDB().add_to_database()

        x = {"email": self.email, "shipping_address": address.id, "card": credit.id}

        try:
            if self.id:
                x["id"] = self.id
        except AttributeError:
            pass

        try:
            if self.actEmail and self.actPassword:
                x["account"] = {"username": self.actEmail, "password": self.actPassword}
                x["account"] = json.dumps(x["account"])
        except AttributeError:
            pass

        return ProfileModel(**x)

    def __repr__(self) -> str:
        return str(self.__dict__)
