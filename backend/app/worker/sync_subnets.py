import asyncio
from datetime import datetime, timezone

import bittensor as bt
from sqlalchemy import select

from app.core.db import SessionLocal, engine
from app.models.subnet_stats import Base, SubnetState
from app.core.bittensor_client import get_subtensor

def sync_subnets_once():
    subtensor = get_subtensor()

    Base.metadata.create_all(bind = engine)

    subnet_uids = subtensor.get_subnets()

    db = SessionLocal()
    try:
        for netuid in subnet_uids:
            subnet = subtensor.subnet(netuid)

            owner_hotkey = subnet.owner_hotkey
            owner_coldkey = subnet.owner_coldkey

            # metagraph for owner incentive (burn rate)
            metagraph = subtensor.metagraph(netuid)
            try:
                owner_uid = metagraph.hotkeys.index(owner_hotkey)
            except ValueError:
                # owner not currently in metagraph – skip or store partial info
                continue

            owner_incentive = float(metagraph.incentive[owner_uid])

            emission = float(subnet.emission.tao) if subnet.emission is not None else None
            alpha_in = float(subnet.alpha_in) if subnet.alpha_in is not None else None
            alpha_out = float(subnet.alpha_out) if subnet.alpha_out is not None else None
            tao_in = float(subnet.tao_in.tao) if subnet.tao_in is not None else None
            alpha_price = float(subnet.price.tao) if subnet.price is not None else None
            moving_price = float(subnet.moving_price) if subnet.moving_price is not None else None

            network_registered_at = int(subnet.network_registered_at)

            row = db.execute(
                select(SubnetState).where(SubnetState.netuid == netuid)
            ).scalar_one_or_none()

            if row is None:
                row = SubnetState(netuid = netuid)
                db.add(row)
            
            row.name = subnet.subnet_name
            row.symbol = subnet.symbol
            row.tempo = int(subnet.tempo)
            row.last_step = int(subnet.last_step)

            row.emission = emission
            row.alpha_in = alpha_in
            row.alpha_out = alpha_out
            row.tao_in = tao_in
            row.alpha_price = alpha_price
            row.moving_price = moving_price


            row.owner_hotkey = owner_hotkey
            row.owner_coldkey = owner_coldkey
            row.owner_uid = owner_uid
            row.owner_incentive = owner_incentive

            row.network_registered_at = network_registered_at
            
            row.updated_at = datetime.now(timezone.utc)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    sync_subnets_once()