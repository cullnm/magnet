# main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import json

app = FastAPI(title="Live Subnets API")

DATA_FILE = Path(__file__).parent / "live_subnets_data.json"


class SubnetInfo(BaseModel):
    netuid: int
    name: str
    network_reg_time: str  # "%Y-%m-%d %H:%M:%S"
    owner_incentive: float
    github: Optional[str] = None
    subnet_url: Optional[str] = None
    price: float
    tao_in: float
    top_miner_reg_time: str  # "%Y-%m-%d %H:%M:%S"
    first_miner_reg_time: str  # "%Y-%m-%d %H:%M:%S"


def load_data() -> list[SubnetInfo]:
    """
    Load fresh data from live_subnets_data.json each time.
    """
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    # Convert each dict into a SubnetInfo model (for validation)
    return [SubnetInfo(**item) for item in raw]


@app.get("/subnets", response_model=List[SubnetInfo])
async def list_subnets():
    """
    Return all live subnets (always fresh from JSON file).
    """
    subnets = load_data()
    return subnets


@app.get("/subnets/{netuid}", response_model=SubnetInfo)
async def get_subnet(netuid: int):
    """
    Return a single subnet by netuid (fresh from JSON file).
    """
    subnets = load_data()
    for subnet in subnets:
        if subnet.netuid == netuid:
            return subnet
    raise HTTPException(status_code=404, detail="Subnet not found")

