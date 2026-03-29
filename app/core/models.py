from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from .database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String, index=True)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Float)
    transaction_type = Column(String)  # DEPOSIT, WITHDRAWAL, TRANSFER_OUT, TRANSFER_IN
    related_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
