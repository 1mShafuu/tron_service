from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class AddressQuery(Base):
    __tablename__ = "address_queries"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))