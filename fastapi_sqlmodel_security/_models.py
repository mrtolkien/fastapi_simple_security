"""SQLModel-based models for both the APIs and the data storage."""
import os
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class UsageLog(SQLModel, table=True):
    __tablename__ = os.getenv("FASTAPI_SQLMODEL_SECURITY_TABLE_NAME", "fastapi_sqlmodel_api_keys")

    api_key: str = Field(primary_key=True)
    name: Optional[str]
    is_active: bool
    never_expire: bool
    expiration_date: datetime
    latest_query_date: Optional[datetime]
    total_queries: int


class UsageLogs(BaseModel):
    logs: List[UsageLog]
