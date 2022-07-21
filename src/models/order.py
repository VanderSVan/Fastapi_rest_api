from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..db.db_sqlalchemy import BaseModel
from .relationships import orders_tables


class OrderModel(BaseModel):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    start_datetime = Column(DateTime, unique=True)
    end_datetime = Column(DateTime, unique=True)
    is_approved = Column(Boolean, default=False)
    cost = Column(Float(precision=2))

    client_id = Column(Integer, ForeignKey('clients.id'))
    tables = relationship('TableModel', secondary=orders_tables, back_populates='orders')


