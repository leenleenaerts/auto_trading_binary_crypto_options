def ctf_approval():
    rpc_url = "xxxxxxxxxxxxxxx"  # Polygon rpc url
    priv_key = "xxxxxxxxxxxxxxx"  # Polygon account private key (needs some MATIC)
    pub_key = "xxxxxxxxxxxxxxx"  # Polygon account public key corresponding to private key

    chain_id = 137

    erc20_approve = """[{"constant": false,"inputs": [{"name": "_spender","type": "address" },{ "name": "_value", "type": "uint256" }],"name": "approve","outputs": [{ "name": "", "type": "bool" }],"payable": false,"stateMutability": "nonpayable","type": "function"}]"""
    erc1155_set_approval = """[{"inputs": [{ "internalType": "address", "name": "operator", "type": "address" },{ "internalType": "bool", "name": "approved", "type": "bool" }],"name": "setApprovalForAll","outputs": [],"stateMutability": "nonpayable","type": "function"}]"""

    usdc_address = "xxxxxxxxxxxxxxxxxxxx"
    ctf_address = "xxxxxxxxxxxxxxxxxxxxxx"

    web3 = Web3(Web3.HTTPProvider(rpc_url))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    nonce = web3.eth.getTransactionCount(pub_key)

    usdc = web3.eth.contract(address=usdc_address, abi=erc20_approve)
    ctf = web3.eth.contract(address=ctf_address, abi=erc1155_set_approval)

    raw_ctf_approval_txn = ctf.functions.setApprovalForAll("xxxxxxxxxxxxxxxxxxx",
                                                           True).buildTransaction(
        {"chainId": chain_id, "from": pub_key, "nonce": nonce})
    signed_ctf_approval_tx = web3.eth.account.sign_transaction(raw_ctf_approval_txn, private_key=priv_key)
    send_ctf_approval_tx = web3.eth.send_raw_transaction(signed_ctf_approval_tx.rawTransaction)
    ctf_approval_tx_receipt = web3.eth.wait_for_transaction_receipt(send_ctf_approval_tx)
    print(ctf_approval_tx_receipt)