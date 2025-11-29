from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- Confirmation Request Schemas ---
class ConfirmationRequestBase(BaseModel):
    type: str # bank, legal, supplier, customer, representation
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

class StandardAccountCreate(StandardAccountBase):
    pass

class StandardAccountRead(StandardAccountBase):
    id: int
    class Config:
        from_attributes = True

class AccountMappingBase(BaseModel):
    client_description: str
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

# --- Engagement Schemas ---
class EngagementBase(BaseModel):
    name: str
    year: int

class EngagementCreate(EngagementBase):
    pass

class EngagementRead(EngagementBase):
    id: int
    client_id: int
    transactions: List[TransactionRead] = []
    # analysis_results: List[AnalysisResultRead] = []

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
    engagements: List[EngagementRead] = []

    class Config:
        from_attributes = True

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_active: bool
    role: str
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

class FirmRegister(BaseModel):
    companyName: str
    cnpj: str
    email: EmailStr
    password: str
