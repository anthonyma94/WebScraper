from operator import add, mod
from webscraper.utility.config import db
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from sqlalchemy.exc import IntegrityError


class ProfileModel(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    shipping_address = db.Column(
        db.Integer, db.ForeignKey("addresses.id"), nullable=False
    )
    credit_card = db.Column(db.Integer, db.ForeignKey("credit_card.id"), nullable=False)


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
    profile = db.relationship("ProfileModel", backref="credit_card", lazy=True)

    def __init__(self, **kwargs):
        super(CreditCardModel, self).__init__(**kwargs)

        if not (CreditCard.is_encrypted(self.card_number)):
            self.card_number = CreditCard.encrypt(self.card_number)

        if self.exp_year < 2000:
            self.exp_year += 2000


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

    @staticmethod
    def fromDB(model: AddressModel):
        return Address(
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
        return AddressModel(
            first_name=self.firstName,
            last_name=self.lastName,
            address=self.address,
            apartment_number=self.apartmentNumber,
            city=self.city,
            province=self.province,
            country=self.country,
            postal_code=self.postalCode,
            phone_number=self.phoneNumber,
            extension=self.extension,
        )


class CreditCard:
    @staticmethod
    def get_public_key():
        with open("public.pem", "r") as f:
            key = f.read()
            return key

    def __init__(
        self,
        firstName,
        lastName,
        creditCardNumber,
        cvv,
        expMonth,
        expYear,
        type,
        billingAddress: Address,
    ):
        self.firstName = firstName
        self.lastName = lastName
        self.creditCardNumber = creditCardNumber
        if CreditCard.is_encrypted(creditCardNumber):
            self.creditCardNumber = CreditCard.decrypt(creditCardNumber)
        self.cvv = cvv
        self.expMonth = expMonth
        self.expYear = expYear
        if int(expYear) < 2000:
            self.expYear = int(expYear) + 2000
        self.type = type
        self.billingAddress = billingAddress

    @property
    def lastFour(self):
        return self.creditCardNumber[-4:]

    @staticmethod
    def fromDB(model: CreditCardModel):
        address = AddressModel.query.get(model.billing_address)
        return CreditCard(
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
        address = self.billingAddress.toDB()
        try:
            db.session.add(address)
            db.session.commit()
        except IntegrityError:
            db.session.flush()
            db.session.rollback()
            address = AddressModel.query.filter_by(
                address=self.billingAddress.address
            ).first()

        return CreditCardModel(
            card_number=CreditCard.encrypt(self.creditCardNumber),
            first_name=self.firstName,
            last_name=self.lastName,
            cvv=self.cvv,
            exp_month=self.expMonth,
            exp_year=self.expYear,
            type=self.type,
            billing_address=address.id,
        )

    @staticmethod
    def is_encrypted(message):
        return len(str(message)) > 16 or str(message)[-1] == "="

    @staticmethod
    def decrypt(ciphertext):
        ciphertext = b64decode(ciphertext.encode("utf-8"))
        f = open("private.pem", "r")
        key = RSA.import_key(f.read())
        f.close()
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
        actEmail,
        actPassword,
        shippingAddress: Address,
        creditCard: CreditCard,
    ):
        self.email = email
        self.shippingAddress = shippingAddress
        self.creditCard = creditCard
        self.actEmail = actEmail
        self.actPassword = actPassword

    @staticmethod
    def fromDB(model: ProfileModel):
        address = AddressModel.query.get(model.shipping_address)
        credit = CreditCardModel.query.get(model.credit_card)
        return ShoppingProfile(
            email=model.email,
            shippingAddress=Address.fromDB(address),
            creditCard=CreditCard.fromDB(credit),
        )

    def toDB(self):
        address = self.shippingAddress.toDB()
        try:
            db.session.add(address)
            db.session.commit()
        except IntegrityError:
            db.session.flush()
            db.session.rollback()
            address = AddressModel.query.filter_by(
                address=self.shippingAddress.address
            ).first()

        credit = self.creditCard.toDB()
        try:
            db.session.add(credit)
            db.session.commit()
        except IntegrityError:
            db.session.flush()
            db.session.rollback()
            credit = CreditCardModel.query.filter_by(
                cvv=self.creditCard.cvv, exp_month=self.creditCard.expMonth
            ).first()

        return ProfileModel(
            email=self.email, shipping_address=address.id, credit_card=credit.id
        )
