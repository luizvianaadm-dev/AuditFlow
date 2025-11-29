from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON, LargeBinary
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
    logo_content = Column(LargeBinary, nullable=True) # Storing logo bytes directly for MVP simplicity

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
    confirmation_requests = relationship("ConfirmationRequest", back_populates="engagement")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    date = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    vendor = Column(String, index=True)
    amount = Column(Float)
    account_code = Column(String, nullable=True, index=True)
    account_name = Column(String, nullable=True, index=True)

    engagement = relationship("Engagement", back_populates="transactions")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    test_type = Column(String) # 'benford', 'duplicates', 'materiality'
    result = Column(JSON)
    executed_at = Column(DateTime, default=datetime.utcnow)
    executed_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    engagement = relationship("Engagement", back_populates="analysis_results")

class StandardAccount(Base):
    __tablename__ = "standard_accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, index=True)
    name = Column(String)
    type = Column(String)

    mappings = relationship("AccountMapping", back_populates="standard_account")

class AccountMapping(Base):
    __tablename__ = "account_mappings"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("audit_firms.id"))
    client_description = Column(String, index=True)
    standard_account_id = Column(Integer, ForeignKey("standard_accounts.id"))

    firm = relationship("AuditFirm", back_populates="account_mappings")
    standard_account = relationship("StandardAccount", back_populates="mappings")

# --- Phase 6.3: Circularization ---

class ConfirmationRequest(Base):
    __tablename__ = "confirmation_requests"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    type = Column(String) # 'bank', 'legal', 'supplier', 'customer', 'representation'
    recipient_name = Column(String)
    recipient_email = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, generated, sent, replied
    created_at = Column(DateTime, default=datetime.utcnow)

    engagement = relationship("Engagement", back_populates="confirmation_requests")
