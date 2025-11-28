from datetime import datetime
from typing import List

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.bittensor_client import get_subtensor
from app.models.subnet_stats import SubnetState
from app.schemas.subnets import SubnetSummary

router = APIRouter(prefix="/subnets", tags=["subnets"])


@router.get("/summary", response_model=List[SubnetSummary])
def get_subnets_summary(
    limit: int = Query(256, ge=1, le=1024), offset: int = Query(0, ge=0)
):
    db = SessionLocal()
    try:
        stmt = (
            select(SubnetState).order_by(SubnetState.netuid.asc()).offset(offset).limit(limit)
        )
        rows: list[SubnetState] = db.execute(stmt).scalars().all()
    finally:
        db.close()
    
    if not rows:
        return []

    subtensor = get_subtensor()
    current_block = int(subtensor.get_current_block())
    now_ts = subtensor.get_timestamp(block = current_block)

    summaries : list[SubnetSummary] = []

    for idx, row in enumerate(rows, start = 1 + offset):
        seconds_to_next_epoch: float | None = None 