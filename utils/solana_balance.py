from solders.rpc.config import RpcAccountInfoConfig
from solana.rpc.api import Client

# 🛰️ Connect to Solana RPC
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
client = Client(SOLANA_RPC)

def get_sol_balance(pubkey):
    client = Client("https://api.mainnet-beta.solana.com")
    try:
        response = client.get_balance(pubkey)
        lamports = response.value  # ✅ Correct way to access balance
        return lamports / 1e9
    except Exception as e:
        print(f"❌ Error fetching balance for {pubkey}: {e}")
        return 0.0
