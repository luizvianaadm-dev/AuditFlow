from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, JSON, LargeBinary, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from src.api.database import Base


class AuditFirm(Base):
    __tablename__ = "audit_firms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    cnpj = Column(String, unique=True, index=True)
    firm_letterhead_url = Column(String, nullable=True) # Timbrado da Firma
    crc_registration = Column(String, nullable=True) # Registro no CRC
    cnai = Column(String, nullable=True) # Cadastro Nacional de Auditores Independentes
    cnai_expiration_date = Column(Date, nullable=True)
    cvm_registration = Column(String, nullable=True) # Registro CVM (Opcional por enquanto)
    email_contact = Column(String, nullable=True) # E-mail de contatos da firma

    clients = relationship("Client", back_populates="firm")
    users = relationship("User", back_populates="firm")
    departments = relationship("Department", back_populates="firm")
    job_roles = relationship("JobRole", back_populates="firm")
    account_mappings = relationship("AccountMapping", back_populates="firm")
    subscription = relationship(
        "Subscription", back_populates="firm", uselist=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="auditor")  # admin, auditor
    # Partner, Manager, Senior, Trainee
    position = Column(String, nullable=True)
    firm_id = Column(Integer, ForeignKey("audit_firms.id"))

    firm = relationship("AuditFirm", back_populates="users")
    engagement_teams = relationship("EngagementTeam", back_populates="user")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    firm_id = Column(Integer, ForeignKey("audit_firms.id"))
    logo_content = Column(LargeBinary, nullable=True)

    firm = relationship("AuditFirm", back_populates="clients")
    engagements = relationship("Engagement", back_populates="client")
    acceptance_forms = relationship("AcceptanceForm", back_populates="client")


class AcceptanceForm(Base):
    __tablename__ = "acceptance_forms"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    independence_check = Column(Boolean, default=False)
    integrity_check = Column(Boolean, default=False)
    competence_check = Column(Boolean, default=False)
    conflict_check = Column(Boolean, default=False)

    status = Column(String, default="pending")
    comments = Column(String, nullable=True)

    client = relationship("Client", back_populates="acceptance_forms")


class Engagement(Base):
    __tablename__ = "engagements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    start_date = Column(DateTime, nullable=True) # Inicio do periodo
    end_date = Column(DateTime, nullable=True)   # Fim do periodo
    service_type = Column(String, default="br_gaap")
    # standard_auditflow, client_custom
    chart_mode = Column(String, default="standard_auditflow")
    client_id = Column(Integer, ForeignKey("clients.id"))

    client = relationship("Client", back_populates="engagements")
    transactions = relationship("Transaction", back_populates="engagement")
    analysis_results = relationship(
        "AnalysisResult", back_populates="engagement")
    confirmation_requests = relationship(
        "ConfirmationRequest", back_populates="engagement")
    team_members = relationship("EngagementTeam", back_populates="engagement")
    workpapers = relationship("WorkPaper", back_populates="engagement")
    mistatements = relationship("Mistatement", back_populates="engagement")
    trial_balance = relationship("TrialBalanceEntry", back_populates="engagement")
    fs_context = relationship("FinancialStatementContext", back_populates="engagement", uselist=False)



class EngagementTeam(Base):
    __tablename__ = "engagement_teams"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role_in_engagement = Column(String)

    engagement = relationship("Engagement", back_populates="team_members")
    user = relationship("User", back_populates="engagement_teams")


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
    test_type = Column(String)
    result = Column(JSON)
    executed_at = Column(DateTime, default=datetime.utcnow)
    executed_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True)

    engagement = relationship("Engagement", back_populates="analysis_results")


class StandardAccount(Base):
    __tablename__ = "standard_accounts"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, index=True)
    name = Column(String)
    type = Column(String)
    template_type = Column(String, default="br_gaap")

    parent_id = Column(Integer, ForeignKey(
        "standard_accounts.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    mappings = relationship(
        "AccountMapping", back_populates="standard_account")
    parent = relationship("StandardAccount", remote_side=[
                          id], backref="children")
    client = relationship("Client")


class AccountMapping(Base):
    __tablename__ = "account_mappings"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("audit_firms.id"))
    client_description = Column(String, index=True)
    client_account_code = Column(String, nullable=True, index=True)
    standard_account_id = Column(Integer, ForeignKey("standard_accounts.id"))

    firm = relationship("AuditFirm", back_populates="account_mappings")
    standard_account = relationship(
        "StandardAccount", back_populates="mappings")


class ConfirmationRequest(Base):
    __tablename__ = "confirmation_requests"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    type = Column(String)
    recipient_name = Column(String)
    recipient_email = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    engagement = relationship(
        "Engagement", back_populates="confirmation_requests")

# --- Phase 7: Audit Work Programs & Mistatements ---


class AuditArea(Base):
    __tablename__ = "audit_areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # e.g. "Caixa e Equivalentes"
    description = Column(String, nullable=True)
    template_type = Column(String, default="br_gaap")

    procedures = relationship("AuditProcedure", back_populates="area")


class AuditProcedure(Base):
    __tablename__ = "audit_procedures"

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("audit_areas.id"))
    description = Column(String)  # e.g. "Circularizar 100% dos bancos"
    required = Column(Boolean, default=True)

    area = relationship("AuditArea", back_populates="procedures")


class WorkPaper(Base):
    __tablename__ = "workpapers"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    procedure_id = Column(Integer, ForeignKey("audit_procedures.id"))

    # open, in_progress, completed, reviewed
    status = Column(String, default="open")
    comments = Column(Text, nullable=True)
    assigned_to_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True)
    reviewed_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)

    engagement = relationship("Engagement", back_populates="workpapers")
    procedure = relationship("AuditProcedure")


class Mistatement(Base):
    __tablename__ = "mistatements"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    workpaper_id = Column(Integer, ForeignKey("workpapers.id"), nullable=True)

    description = Column(String)
    amount_divergence = Column(Float)  # The numeric difference
    type = Column(String)  # factual, judgmental, projected
    status = Column(String, default="open")  # open, adjusted, unadjusted

    engagement = relationship("Engagement", back_populates="mistatements")

# --- Billing ---


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # Basic, Pro, Enterprise
    price = Column(Float)
    description = Column(String)
    features = Column(JSON)  # List of feature strings

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    firm_id = Column(Integer, ForeignKey("audit_firms.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    status = Column(String, default="active")  # active, canceled, past_due
    start_date = Column(DateTime, default=datetime.utcnow)
    current_period_end = Column(DateTime)

    firm = relationship("AuditFirm", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    amount = Column(Float)
    status = Column(String)  # paid, failed
    date = Column(DateTime, default=datetime.utcnow)
    invoice_url = Column(String, nullable=True)

    subscription = relationship("Subscription", back_populates="payments")

class TrialBalanceEntry(Base):
    __tablename__ = "trial_balance_entries"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))
    account_code = Column(String, index=True)
    account_name = Column(String)

    # Balances
    initial_balance = Column(Float, default=0.0)
    debits = Column(Float, default=0.0)
    credits = Column(Float, default=0.0)
    final_balance = Column(Float, default=0.0)

    engagement = relationship("Engagement", back_populates="trial_balance")

class FinancialStatementContext(Base):
    __tablename__ = "fs_contexts"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"))

    # Storing the structured JSON data for Blocks 1-5
    # Identification, Period, Operational Context, Base of Prep, Practices
    context_data = Column(JSON, default={})

    # Status
    status = Column(String, default="draft") # draft, reviewed, final
    updated_at = Column(DateTime, default=datetime.utcnow)

    engagement = relationship("Engagement", back_populates="fs_context")
