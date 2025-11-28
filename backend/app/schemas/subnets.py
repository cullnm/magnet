from datetime import datetime
from pydantic import BaseModel

class SubnetSummary(BaseModel):
    no: int
    netuid : int
    
    burn_rate: float | None
    emission : float | None
    alpha_price : float | None

    issue_datetime : datetime | None
    minutes_to_next_epoch : float | None

    class Config:
        from_attributes = True