import sqlalchemy as db
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = db.create_engine("sqlite:///database.db", echo=True)

# Create database and table
Base = declarative_base()

Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    public_id = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}'>"

# Session = sessionmaker(bind=engine)

# session = Session()

# user1 = User(email="test@123.com", username="test123")

# session.add(user1)
# session.commit()

# query = session.query(User).all()

# for row in query:
#     print(repr(row))
