
# from app.core.bittensor_client import get_subtensor
import bittensor as bt

subtensor = bt.subtensor()

current_block = subtensor.get_current_block()
current_ts = subtensor.get_timestamp()

subnet_uids = subtensor.get_subnets()

for netuid in subnet_uids:
    subnet = subtensor.subnet(netuid)

    owner_hotkey = subnet.owner_hotkey
    owner_coldkey = subnet.owner_coldkey

    metagraph = subtensor.metagraph(netuid)
    try:
        owner_uid = metagraph.hotkeys.index(owner_hotkey)
    except ValueError:
        continue
        raise RuntimeError(
            f"Subnet owner hotkey {owner_hotkey} not found in metagraph for netuid={netuid}"
        )

    owner_incentive = float(metagraph.incentive[owner_uid])

    print(netuid, subnet)