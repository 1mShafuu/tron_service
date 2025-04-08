from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AddressRequest(BaseModel):
    address: str


class AddressInfoResponse(BaseModel):
    address: str
    balance: int
    bandwidth: int
    energy: int


class QueryResponse(BaseModel):
    id: int
    address: str
    status: str
    error_message: Optional[str]
    created_at: datetime
