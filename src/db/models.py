from sqlalchemy import Column, Integer, String

from .postgres import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, index=True)
    count= Column(Integer, default=0)
    