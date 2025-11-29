from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.api.database import Base

class AuditFirm(Base):
    __tablename__ = "audit_firms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cnpj = Column(String, unique=True, index=True)

    clients = relationship("Client", back_populates="firm")
    users = relationship("User", back_populates="firm")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="auditor") # admin, auditor
    firm_id = Column(Integer, ForeignKey("audit_firms.id"))

    firm = relationship("AuditFirm", back_populates="users")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    firm_id = Column(Integer, ForeignKey("audit_firms.id"))

    firm = relationship("AuditFirm", back_populates="clients")
    engagements = relationship("Engagement", back_populates="client")

class Engagement(Base):
    __tablename__ = "engagements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # e.g. "Auditoria 2024"
    year = Column(Integer)
    client_id = Column(Integer, ForeignKey("clients.id"))

    client = relationship("Client", back_populates="engagements")
    transactions = relationship("Transaction", back_populates="engagement")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    date = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    vendor = Column(String, index=True)
    amount = Column(Float)

    engagement = relationship("Engagement", back_populates="transactions")
