from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.bittensor_client import get_current_block
from app.api import subnets

app = FastAPI(title = "Magnet Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.BACKEND_CORS_ORIGINS,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.get("/health")
def health():
    return {"status" : "ok"}

@app.get("/chain/info")
def chain_info():
    block = get_current_block()
    return {
        "network" : settings.BITTENSOR_NETWORK,
        "current_block" : block,
    }
app.include_router(subnets.router)