from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# --- Transaction Schemas ---
class TransactionBase(BaseModel):
    vendor: str
    amount: float
    description: Optional[str] = None
    date: Optional[datetime] = None

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
