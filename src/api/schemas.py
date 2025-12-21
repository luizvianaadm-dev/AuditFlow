from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Dict
from datetime import datetime, date

# --- Engagement Schemas ---
class EngagementBase(BaseModel):
    name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    service_type: str = "br_gaap" # br_gaap, condo_audit, condo_ppa

class EngagementCreate(EngagementBase):
    chart_mode: Optional[str] = "standard_auditflow"

class EngagementRead(EngagementBase):
    id: int
    client_id: int
    chart_mode: str = "standard_auditflow"
    client_letterhead_url: Optional[str] = None
    transactions: List['TransactionRead'] = []

    class Config:
        from_attributes = True

# --- Transaction Schemas ---
class TransactionBase(BaseModel):
    vendor: str
    amount: float
    description: Optional[str] = None
    date: Optional[datetime] = None
    account_code: Optional[str] = None
    account_name: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
    engagement_id: int

    class Config:
        from_attributes = True

# Need to update EngagementRead to recognize TransactionRead which is defined after it in this file order?
# Pydantic handles forward refs with strings or Rebuild.
# But for simplicity, I reordered them. Wait, TransactionRead is used in EngagementRead.
# So TransactionRead must be defined BEFORE EngagementRead.

# Re-ordering file content:

class TransactionReadForward(TransactionBase):
    id: int
    engagement_id: int
    class Config:
        from_attributes = True

class EngagementReadForward(EngagementBase):
    id: int
    client_id: int
    transactions: List[TransactionReadForward] = []
    class Config:
        from_attributes = True

# --- Acceptance Schemas ---
class AcceptanceFormBase(BaseModel):
    independence_check: bool
    integrity_check: bool
    competence_check: bool
    conflict_check: bool
    comments: Optional[str] = None

class AcceptanceFormCreate(AcceptanceFormBase):
    pass

class AcceptanceFormRead(AcceptanceFormBase):
    id: int
    client_id: int
    created_by_user_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Team Schemas ---
class UserUpdate(BaseModel):
    position: Optional[str] = None
    role: Optional[str] = None

class UserInvite(BaseModel):
    email: EmailStr
    password: str
    role: str = "auditor"
    position: str = "Trainee"

# --- Confirmation Request Schemas ---
class ConfirmationRequestBase(BaseModel):
    type: str
    recipient_name: str
    recipient_email: Optional[str] = None

class ConfirmationRequestCreate(ConfirmationRequestBase):
    pass

class ConfirmationRequestRead(ConfirmationRequestBase):
    id: int
    engagement_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Standard Account & Mapping Schemas ---
class StandardAccountBase(BaseModel):
    code: str
    name: str
    type: str
    template_type: str
    level: int = 1
    parent_id: Optional[int] = None
    client_id: Optional[int] = None

class StandardAccountCreate(StandardAccountBase):
    pass

class StandardAccountRead(StandardAccountBase):
    id: int
    class Config:
        from_attributes = True

class AccountMappingBase(BaseModel):
    client_description: str
    client_account_code: Optional[str] = None
    standard_account_id: int

class AccountMappingCreate(AccountMappingBase):
    pass

class AccountMappingRead(AccountMappingBase):
    id: int
    firm_id: int
    standard_account: Optional[StandardAccountRead] = None
    class Config:
        from_attributes = True

# --- Analysis Schemas ---
class AnalysisResultBase(BaseModel):
    test_type: str
    result: Dict[str, Any]

class AnalysisResultCreate(AnalysisResultBase):
    pass

class AnalysisResultRead(AnalysisResultBase):
    id: int
    engagement_id: int
    executed_at: datetime
    executed_by_user_id: Optional[int]

    class Config:
        from_attributes = True

# --- Client Schemas ---
class ClientBase(BaseModel):
    name: str

class ClientCreate(ClientBase):
    firm_id: int

class ClientRead(ClientBase):
    id: int
    firm_id: int
    engagements: List[EngagementReadForward] = []

    class Config:
        from_attributes = True

# --- Department & Role Schemas ---
class DepartmentBase(BaseModel):
    name: str
    is_overhead: bool = True

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    id: int
    firm_id: int
    class Config:
        from_attributes = True

class JobRoleBase(BaseModel):
    name: str
    level: int
    hourly_rate: float = 0.0

class JobRoleCreate(JobRoleBase):
    pass

class JobRoleRead(JobRoleBase):
    id: int
    firm_id: int
    class Config:
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    role: Optional[str] = "auditor" # Legacy role, keep for Auth

class UserCreate(UserBase):
    password: str
    cpf: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    admission_date: Optional[date] = None
    
    department_id: Optional[int] = None
    job_role_id: Optional[int] = None

class UserInvite(UserBase):
    password: str
    cpf: str
    phone: str
    birthday: date
    admission_date: date
    
    department_id: int
    job_role_id: int

class UserRead(UserBase):
    id: int
    is_active: bool
    role: str
    
    # Profile
    cpf: Optional[str] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    admission_date: Optional[date] = None
    
    department_id: Optional[int] = None
    job_role_id: Optional[int] = None
    department: Optional[DepartmentRead] = None
    job_role: Optional[JobRoleRead] = None
    
    firm_id: int

    class Config:
        from_attributes = True

# --- AuditFirm Schemas ---
class AuditFirmBase(BaseModel):
    name: str
    cnpj: str

class AuditFirmCreate(AuditFirmBase):
    pass

class AuditFirmRead(AuditFirmBase):
    id: int
    firm_letterhead_url: Optional[str] = None
    crc_registration: Optional[str] = None
    cnai: Optional[str] = None
    cnai_expiration_date: Optional[date] = None
    cvm_registration: Optional[str] = None
    users: List[UserRead] = []
    clients: List[ClientRead] = []

    class Config:
        from_attributes = True

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class PasswordResetRequest(BaseModel):
    token: str
    new_password: str

class FirmRegister(BaseModel):
    companyName: str
    cnpj: str
    email: EmailStr
    password: str
    crc_registration: Optional[str] = None
    cnai: Optional[str] = None
    cnai_expiration_date: Optional[date] = None
    cvm_registration: Optional[str] = None
    termsAccepted: bool = False
    
    # Profile of the Initial Admin
    cpf: Optional[str] = None
    phone: Optional[str] = None

# --- Financial Statements Schemas ---
class CashFlowItem(BaseModel):
    description: str
    value: float

class CashFlowInput(BaseModel):
    operating_adjustments: List[CashFlowItem] = []
    investment_activities: List[CashFlowItem] = []
    financing_activities: List[CashFlowItem] = []
