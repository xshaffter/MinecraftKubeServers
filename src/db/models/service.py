from common.fastapi.db import Base
from sqlalchemy import Column, String, Boolean, DateTime


class Service(Base):
    service_path = Column(String)
    service_type = Column(String)
    is_active = Column(Boolean, default=True)
    service_name = Column(String)
    started_at = Column(DateTime)
    stopped_at = Column(DateTime, nullable=True)
    used_port = Column(String)
