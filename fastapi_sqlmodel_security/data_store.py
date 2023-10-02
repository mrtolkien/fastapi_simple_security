"""Data store for the API keys and usage logs."""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional

from sqlmodel import Session, SQLModel, create_engine, select

from fastapi_sqlmodel_security._models import UsageLog
from fastapi_sqlmodel_security._security_secret import generate_expiration_date, generate_secret_key


class DataStore(ABC):
    """Abstract base class for the data store."""

    @abstractmethod
    def create_key(self, name: str, never_expire: bool) -> str:
        pass

    @abstractmethod
    def renew_key(self, api_key: str, new_expiration_date: Optional[date] = None) -> bool:
        pass

    @abstractmethod
    def revoke_key(self, api_key: str) -> bool:
        pass

    @abstractmethod
    def check_key(self, api_key: str) -> bool:
        pass

    @abstractmethod
    def get_usage_stats(self) -> List[UsageLog]:
        pass


class SqlModelDataStore(DataStore):
    """Data store using SQLModel."""

    def __init__(self, conn_url: str = None, engine = None) -> None:
        if conn_url:
            self.engine = create_engine(conn_url)
        else:
            self.engine = engine

        SQLModel.metadata.create_all(self.engine)

    def create_key(self, name: str, never_expire: bool) -> str:
        with Session(self.engine) as session:
            new_key = UsageLog(
                api_key=generate_secret_key(),
                name=name,
                is_active=True,
                never_expire=never_expire,
                expiration_date=generate_expiration_date(),
                latest_query_date=None,
                total_queries=0,
            )
            session.add(new_key)
            session.commit()
            return new_key.api_key


    def renew_key(self, api_key: str, new_expiration_date: Optional[date]) -> bool:
        with Session(self.engine) as session:
            stmt = select(UsageLog).where(UsageLog.api_key == api_key)
            key = session.exec(stmt).one_or_none()
            if key:
                key.expiration_date = generate_expiration_date(new_expiration_date)
                key.is_active = True
                session.add(key)
                session.commit()
                return True
            else:
                return False

    def revoke_key(self, api_key: str) -> bool:
        with Session(self.engine) as session:
            stmt = select(UsageLog).where(UsageLog.api_key == api_key)
            key = session.exec(stmt).one_or_none()
            if key:
                key.is_active = False
                session.add(key)
                session.commit()
                return True
            else:
                return False

    def check_key(self, api_key: str) -> bool:
        with Session(self.engine) as session:
            stmt = select(UsageLog).where(UsageLog.api_key == api_key)
            key = session.exec(stmt).one_or_none()
            if key and key.is_active:
                key.latest_query_date = datetime.now()
                key.total_queries += 1
                session.add(key)
                session.commit()
                return True
            else:
                return False

    def get_usage_stats(self) -> List[UsageLog]:
        with Session(self.engine) as session:
            stmt = select(UsageLog)
            return session.exec(stmt).all()
