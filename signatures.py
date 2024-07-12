import requests
import json
from time import sleep

# Solana RPC endpoint
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# Address to track
ENTRY_POINT = "cmUT9D8w3FQ9SxZHM8Kwrfjyi1Cy9BGR9ndnp2ZsuV7"
ADDRESS = "3Q3pE1izgCeAtTR23eufZy5vCEGtpWLBQcGD2HGd1cbU"

# Helper function to get transaction signatures for an address with pagination
def get_transaction_signatures(address, limit=1000):
    headers = {
        "Content-Type": "application/json"
    }
    all_signatures = []
    last_signature = None

    while True:
        params = {
            "limit": limit
        }
        if last_signature:
            params["before"] = last_signature

        payload = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getConfirmedSignaturesForAddress2",
            "params": [
                address,
                params
            ]
        })

        response = requests.post(SOLANA_RPC_URL, headers=headers, data=payload)
        response.raise_for_status()
        result = response.json().get('result', [])

        if not result:
            break

        signatures = [sig['signature'] for sig in result]
        all_signatures.extend(signatures)
        last_signature = result[-1]['signature']

        # Break if we have fetched less than the limit (no more transactions)
        if len(result) < limit:
            break

    return all_signatures

# Helper function to get transaction details for a signature
def get_transaction_details(signature):
    headers = {
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getConfirmedTransaction",
        "params": [
            signature
        ]
    })

    response = requests.post(SOLANA_RPC_URL, headers=headers, data=payload)
    response.raise_for_status()
    return response.json().get('result')

# Extract amounts from transaction details and update balance
def update_balance(transaction, balance):
    pre_balances = transaction['meta']['preTokenBalances']
    post_balances = transaction['meta']['postTokenBalances']

    for pre, post in zip(pre_balances, post_balances):
        if pre['owner'] == ADDRESS:
            continue
        pre_amount = pre['uiTokenAmount']['uiAmount'] if pre['uiTokenAmount']['uiAmount'] else 0
        post_amount = post['uiTokenAmount']['uiAmount'] if post['uiTokenAmount']['uiAmount'] else 0
        change = pre_amount - post_amount
        balance[pre['owner']] = balance.get(pre['owner'], 0) - change

if __name__ == "__main__":
    balance = {}
    signatures = get_transaction_signatures(ENTRY_POINT)
    # write signatures to signatures.txt
    with open("signatures.txt", "w") as f:
        for signature in signatures:
            f.write(signature + "\n")
