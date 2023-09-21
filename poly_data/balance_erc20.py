import os
from web3 import Web3


erc20balance_of = abi = '[{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"minter_","type":"address"},...'

DECIMALS = 10 ** 6  # Number of decimals used by the Outcome Token


def main():
    rpc_url = "https://polygon-rpc.com"

    w3 = Web3(Web3.HTTPProvider(rpc_url))

    print(f"Starting...")

    ctf_address = w3.to_checksum_address("xxxxxxxxxxxxxx")
    token_id = xxxxxxxxxxxxxxxx
    owner = w3.to_checksum_address("xxxxxxxxxxxxxxxxxxxxxx")  # the address to check

    ctf = w3.eth.contract(ctf_address, abi=abi)
    try:
        raw_balance = ctf.functions.balanceOf(token_id).call()
        balance_formatted = float(raw_balance / DECIMALS)
        print(f"CTF Balance of {owner} for {token_id}: {str(balance_formatted)}")
    except Exception as e:
        print(f"Error querying CTF balance : {e}")
        raise e

    print("Done!")


main()