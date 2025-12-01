
# from app.core.bittensor_client import get_subtensor
import bittensor as bt

subtensor = bt.subtensor()
archive_subtensor = bt.subtensor('archive')

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

    tao_in = subnet.tao_in
    price = subnet.price
    network_reg_time = archive_subtensor.get_timestamp(subnet.network_registered_at)
    try:
        github = subnet.subnet_identity.github_repo
        subnet_url = subnet.subnet_identity.subnet_url
    except Exception as e:
        github = ""
        subnet_url = ""
    
    # print(netuid, subnet)

    print(f"{netuid},  {subnet.subnet_name},  {network_reg_time},  {owner_incentive},  {github},  {subnet_url},  {price},  {tao_in}")