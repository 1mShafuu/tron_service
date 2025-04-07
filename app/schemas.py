from pydantic import BaseModel
from datetime import datetime


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
    error_message: str | None
    created_at: datetime
