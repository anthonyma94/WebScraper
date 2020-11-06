import json, os
from Crypto.PublicKey import RSA
from webscraper.models.tasks import TaskModel
from webscraper.models.profiles import Address, CreditCard, ShoppingProfile
from webscraper.models.bestbuy import BestBuy
from webscraper.models.products import ProductModel
from flask import Flask
from flask_restful import Api
from webscraper.utility.utils import db
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.exc import IntegrityError

if find_dotenv():
    load_dotenv(find_dotenv())

if not os.path.isfile("./public.pem") or not os.path.isfile("./private.pem"):
    key = RSA.generate(4096)
    private_key = key.export_key()
    with open("private.pem", "wb") as f:
        f.write(private_key)

    public_key = key.publickey().export_key()
    with open("public.pem", "wb") as f:
        f.write(public_key)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///../../database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app._static_folder = "../public/static"
api = Api(app)


with app.app_context():
    db.init_app(app)
    engine = db.get_engine()
    if not (ProductModel.metadata.tables[ProductModel.__tablename__].exists(engine)):
        db.create_all()

    if app.config["ENV"].lower() == "development":

        profile = ShoppingProfile(
            email="anthonyma940603@gmail.com",
            actEmail="anthonyma940603@gmail.com",
            actPassword="8290F9AF",
            shippingAddress=Address(
                address="3692 Water St",
                city="Kitchener",
                firstName="Test",
                lastName="Test",
                phoneNumber="2894439715",
                province="ON",
                postalCode="N2H5A5",
            ),
            creditCard=CreditCard(
                firstName="Test",
                lastName="Test",
                creditCardNumber="4263982640269299",
                cvv="837",
                expMonth="2",
                expYear="2023",
                type="VISA",
                billingAddress=Address(
                    address="3692 Water St",
                    city="Kitchener",
                    firstName="Test",
                    lastName="Test",
                    phoneNumber="2894439715",
                    province="ON",
                    postalCode="N2H5A5",
                ),
            ),
        )

        model = profile.toDB().add_to_database()

        try:
            item = (
                BestBuy(
                    "https://www.bestbuy.ca/en-ca/product/acer-spin-11-6-touchscreen-2-in-1-chromebook-silver-mediatek-m8183-64gb-ssd-4gb-ram-chrome-os/14742355"
                )
                .toDB()
                .add_to_database(silent=False)
            )
            task = TaskModel(
                product=item.id,
                price_limit=1.99,
                purchase=False,
                notify_on_available=False,
                profile=model.id,
            ).add_to_database(silent=False)
        except IntegrityError:
            pass

        try:
            with open("realprofile.json", "r") as f:
                result = json.load(f)

            shippingAddress = Address(**result["shippingAddress"])
            billingAddress = Address(**result["creditCard"]["billingAddress"])

            result["creditCard"]["billingAddress"] = billingAddress
            result["shippingAddress"] = shippingAddress
            card = CreditCard(**result["creditCard"])

            result["creditCard"] = card

            profile = ShoppingProfile(**result)

            profile.toDB().add_to_database()
        except Exception:
            pass
