from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..db.db_sqlalchemy import BaseModel
from .relationships import orders_tables


class OrderModel(BaseModel):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    status = Column(String(length=100))
    cost = Column(Float(precision=2))

    client_id = Column(Integer, ForeignKey('clients.id', onupdate='CASCADE', ondelete='CASCADE'))
    tables = relationship('TableModel', secondary=orders_tables, back_populates='orders')


