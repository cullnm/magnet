from functools import lru_cache
from typing import Optional

import bittensor as bt

from app.core.config import settings


@lru_cache(maxsize=1)
def get_subtensor() -> bt.subtensor:
    if settings.BITTENSOR_ARCHIEVE_ENDPOINT:
        return bt.subtensor(chain_endpoint=settings.BITTENSOR_ARCHIEVE_ENDPOINT)
    else:
        return bt.subtensor(
            network = settings.BITTENSOR_NETWORK
        )

def get_current_block() -> int:
    st = get_subtensor()
    return int(st.get_current_block())