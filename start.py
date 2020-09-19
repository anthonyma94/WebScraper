from webscraper.server.database import UserModel
from webscraper.server import db


if __name__ == "__main__":
    db.create_all()
    admin = UserModel(
        username="admin", password="password", email="admin@admin.com", is_admin=True
    )
    db.session.add(admin)
    db.session.commit()