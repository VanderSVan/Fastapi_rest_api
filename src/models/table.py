from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship

from src.db.db_sqlalchemy import BaseModel
from src.models.relationships import orders_tables


class TableModel(BaseModel):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True)
    type = Column(String(length=50))
    number_of_seats = Column(Integer)
    price_per_hour = Column(Float(precision=2))

    orders = relationship('OrderModel', secondary=orders_tables, back_populates='tables')
