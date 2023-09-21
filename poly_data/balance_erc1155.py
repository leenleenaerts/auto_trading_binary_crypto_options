import os
from web3 import Web3


erc1155_balance_of = """[{"inputs": [{"internalType": "address","name": "account","type": "address"},{"internalType": "uint256","name": "id","type": "uint256"}],"name": "balanceOf","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"}]"""

DECIMALS = 10 ** 6  # Number of decimals used by the Outcome Token


def main():
    rpc_url = "https://polygon-rpc.com"

    w3 = Web3(Web3.HTTPProvider(rpc_url))

    print(f"Starting...")

    ctf_address = w3.to_checksum_address("xxxxxxxxxxxxxxxxx")
    token_id = xxxxxxxxxxxxxxxxxxx
    owner = w3.to_checksum_address("xxxxxxxxxxxxxxxxxxxxx")  # the address to check

    ctf = w3.eth.contract(ctf_address, abi=erc1155_balance_of)
    try:
        raw_balance = ctf.functions.balanceOf(owner, token_id).call()
        balance_formatted = float(raw_balance / DECIMALS)
        print(f"CTF Balance of {owner} for {token_id}: {str(balance_formatted)}")
    except Exception as e:
        print(f"Error querying CTF balance : {e}")
        raise e

    print("Done!")


main()