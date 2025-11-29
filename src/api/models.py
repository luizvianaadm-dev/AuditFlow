from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON
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
    account_mappings = relationship("AccountMapping", back_populates="firm")

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
    analysis_results = relationship("AnalysisResult", back_populates="engagement")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    date = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    vendor = Column(String, index=True)
    amount = Column(Float)

    # New fields for Phase 6
    account_code = Column(String, nullable=True, index=True) # From CSV
    account_name = Column(String, nullable=True, index=True) # From CSV

    engagement = relationship("Engagement", back_populates="transactions")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    test_type = Column(String) # 'benford', 'duplicates'
    result = Column(JSON)
    executed_at = Column(DateTime, default=datetime.utcnow)
    executed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    engagement = relationship("Engagement", back_populates="analysis_results")

# --- Phase 6.1: Standard Accounts & Mapping ---

class StandardAccount(Base):
    __tablename__ = "standard_accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, index=True) # e.g., "1.1.01"
    name = Column(String) # e.g., "Caixa e Equivalentes"
    type = Column(String) # Asset, Liability, Equity, Revenue, Expense

    mappings = relationship("AccountMapping", back_populates="standard_account")

class AccountMapping(Base):
    __tablename__ = "account_mappings"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("audit_firms.id")) # Mappings are specific to a Firm (learning)
    client_description = Column(String, index=True) # The string found in the CSV (e.g. "Bco Brasil")
    standard_account_id = Column(Integer, ForeignKey("standard_accounts.id"))

    firm = relationship("AuditFirm", back_populates="account_mappings")
    standard_account = relationship("StandardAccount", back_populates="mappings")
