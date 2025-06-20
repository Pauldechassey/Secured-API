from sqlalchemy import Column, Integer, String, ForeignKey
from db import Base


class ParsedURL(Base):
    __tablename__ = "parsed_urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String)
    scheme = Column(String, nullable=True)
    netloc = Column(String, nullable=True)
    hostname = Column(String, nullable=True)
    port = Column(String, nullable=True)
    path = Column(String, nullable=True)
    query = Column(String, nullable=True)
    query_string = Column(String, nullable=True)
    fragment = Column(String, nullable=True)
    user_email = Column(String, ForeignKey("users.email"))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    fullname = Column(String)
    hashed_password = Column(String)
