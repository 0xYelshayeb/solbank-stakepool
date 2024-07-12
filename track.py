import requests
import json
from time import sleep

# Solana RPC endpoint
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# Address to track
ENTRY_POINT = "cmUT9D8w3FQ9SxZHM8Kwrfjyi1Cy9BGR9ndnp2ZsuV7"
ADDRESS = "3Q3pE1izgCeAtTR23eufZy5vCEGtpWLBQcGD2HGd1cbU"

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
    # read signatures from signatures.txt
    with open("signatures.txt", "r") as f:
        signatures = f.read().splitlines()

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

    # Print a summary of balances
    print("\nSummary of Balances:")
    for owner, bal in balance.items():
        print(f"Owner: {owner}, Balance: {bal:.6f}")
