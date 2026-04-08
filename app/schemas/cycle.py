from pydantic import BaseModel
from datetime import date
from typing import Optional

class CycleResponse(BaseModel):
    id_cycle: int
    start_date: Optional[date]
    end_date: Optional[date]

    class Config:
        from_attributes = True