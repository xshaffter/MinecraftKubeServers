from pydantic import BaseModel

from src.db.models.enums import Modality


class WorldData(BaseModel):
    world_type: Modality
    world_path: str
    world_identifier: int
    is_active: bool
