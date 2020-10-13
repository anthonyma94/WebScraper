from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode


class ShoppingProfile:
    def __init__(
        self,
        address,
        city,
        country,
        email,
        firstName,
        lastName,
        phoneNumber,
        postalCode,
        province,
        creditCardNumber,
        cvv,
        expMonth,
        expYear,
        apartmentNumber=None,
        extension=None,
    ):
        self.address = address
        self.apartmentNumber = apartmentNumber
        self.city = city
        self.country = country
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.phoneNumber = phoneNumber
        self.extension = extension
        self.postalCode = postalCode
        self.province = province
        self.creditCardNumber = creditCardNumber
        self.cvv = cvv
        self.expMonth = expMonth
        self.expYear = expYear
        pass


class CreditCard:
    @staticmethod
    def get_public_key():
        with open("public.pem", "r") as f:
            key = f.read()
            return key

    def __init__(self, creditCardNumber, cvv, expMonth, expYear):
        self.creditCardNumber = creditCardNumber
        self.cvv = cvv
        self.expMonth = expMonth
        self.expYear = expYear

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
    def encrypt(message):
        """Encrypts a given message using SHA-1

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