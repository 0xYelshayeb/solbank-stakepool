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
        print(all_signatures)

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
    print(f"Found {len(signatures)} transactions for {ENTRY_POINT}")

    for i in range(len(signatures)):

        if i % 10 == 0:
            # Print a summary of balances
            print(f"\nSummary of Balances for {i} transactions:")
            for owner, bal in balance.items():
                print(f"Owner: {owner}, Balance: {bal:.6f}")

        sleep(2)
        transaction = get_transaction_details(signatures[i])
        if transaction:
            update_balance(transaction, balance)
            # Log the transaction details
            pre_balances = transaction['meta']['preTokenBalances']
            post_balances = transaction['meta']['postTokenBalances']
            
            for pre, post in zip(pre_balances, post_balances):
                if pre['owner'] == ADDRESS or post['owner'] == ADDRESS:
                    pre_amount = pre['uiTokenAmount']['uiAmount'] if pre['uiTokenAmount']['uiAmount'] else 0
                    change = float(post['uiTokenAmount']['uiAmount']) - pre_amount
                    involved_addresses = [pre['owner'], post['owner']]
                    print(f"Transaction Signature: {signatures[i]}")
                    print(f"Balance Change: {change:.6f}")
                    print("-" * 40)

    # Print a summary of balances
    print("\nSummary of Balances:")
    for owner, bal in balance.items():
        print(f"Owner: {owner}, Balance: {bal:.6f}")
