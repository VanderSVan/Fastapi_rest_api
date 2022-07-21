from sqlalchemy import Column, Integer, String

from ..db.db_sqlalchemy import BaseModel


class ClientModel(BaseModel):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    email = Column(String(length=100), unique=True, index=True)
    phone = Column(String(length=15), unique=True)
