from common.fastapi.db import Base
from sqlalchemy import Column, String, Boolean, Integer


class World(Base):
    world_path = Column(String)
    world_type = Column(String)
    world_identifier = Column(Integer)
    is_active = Column(Boolean, default=True)
