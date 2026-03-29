from pydantic import BaseModel
from datetime import datetime

class AccountBase(BaseModel):
    owner: str

class AccountCreate(AccountBase):
    pass

class AccountRead(AccountBase):
    id: int
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True
