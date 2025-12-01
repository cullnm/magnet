from datetime import datetime
import time
import bittensor as bt
import json
import numpy as np


while True:
    try:

        subtensor = bt.subtensor()
        archive_subtensor = bt.subtensor('archive')

        current_block = subtensor.get_current_block()
        current_ts = subtensor.get_timestamp()

        subnet_uids = subtensor.get_subnets()
        
        subnets_info = []

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
            
            incentives = np.array(
                metagraph.incentive.tolist()
                if hasattr(metagraph.incentive, "tolist")
                else metagraph.incentive
            )
            reg_blocks = np.array(
                metagraph.block_at_registration.tolist()
                if hasattr(metagraph.block_at_registration, "tolist")
                else metagraph.block_at_registration
            )
            validator_permit = np.array(
                metagraph.validator_permit.tolist()
                if hasattr(metagraph.validator_permit, "tolist")
                else metagraph.validator_permit
            ).astype(bool)

            owner_incentive = float(incentives[owner_uid])

            miners_mask = ~validator_permit
            
            # ---- earliest miner registration time (optional) ----
            if np.any(miners_mask):
                miner_blocks = reg_blocks[miners_mask]
                first_miner_block = int(miner_blocks.min())
                first_miner_time = archive_subtensor.get_timestamp(first_miner_block)
                first_miner_time_str = first_miner_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                first_miner_block = None
                first_miner_time_str = None

            # ---- TOP INCENTIVE MINER REGISTRATION TIME ----
            if np.any(miners_mask):
                miner_incentives = incentives[miners_mask]

                # index *within miners* with max incentive
                top_miner_local_idx = int(np.argmax(miner_incentives))

                # global uid index: indices of all miners, then pick local index
                all_indices = np.arange(incentives.shape[0])
                miner_indices = all_indices[miners_mask]
                top_miner_uid = int(miner_indices[top_miner_local_idx])

                top_miner_block = int(reg_blocks[top_miner_uid])
                top_miner_time = archive_subtensor.get_timestamp(top_miner_block)
                top_miner_time_str = top_miner_time.strftime("%Y-%m-%d %H:%M:%S")

                top_miner_hotkey = metagraph.hotkeys[top_miner_uid]
            else:
                top_miner_uid = None
                top_miner_block = None
                top_miner_time_str = None
                top_miner_hotkey = None


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

            # print(
            #     f"{netuid}, {subnet.subnet_name}, "
            #     f"network_reg_time={network_reg_time}, "
            #     f"first_miner_block={first_miner_block}, "
            #     f"first_miner_time={first_miner_time_str}, "
            #     f"top_miner_uid={top_miner_uid}, "
            #     f"top_miner_block={top_miner_block}, "
            #     f"top_miner_time={top_miner_time_str}, "
            #     f"top_miner_hotkey={top_miner_hotkey}, "
            #     f"owner_incentive={owner_incentive}, "
            #     f"{github}, {subnet_url}, {price}, {tao_in}"
            # )
            subnets_info.append(
                {
                    "netuid" : netuid,
                    "name" : subnet.subnet_name,
                    "reg_time" : network_reg_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "owner_incentive" : owner_incentive,
                    "github" : github,
                    "subnet_url" : subnet_url,
                    "price" : price.tao,
                    "tao_in" : tao_in.tao
                }
            )
            subnets_info.append(
                {
                    "netuid": netuid,
                    "name": subnet.subnet_name,
                    "network_reg_time": network_reg_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "first_miner_block": first_miner_block,
                    "first_miner_reg_time": first_miner_time_str,
                    "top_miner_uid": top_miner_uid,
                    "top_miner_block": top_miner_block,
                    "top_miner_reg_time": top_miner_time_str,
                    "top_miner_hotkey": top_miner_hotkey,
                    "owner_incentive": owner_incentive,
                    "github": github,
                    "subnet_url": subnet_url,
                    "price": price.tao,
                    "tao_in": tao_in.tao,
                }
            )
        # print(subnets_info)
        with open("live_subnets_data.json", "w") as f:
            json.dump(subnets_info, f)
    except Exception as e:
        print(e)
    time.sleep(100)