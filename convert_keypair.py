import base58
from solders.keypair import Keypair

# Your raw 64-byte secret key
key_bytes = bytes([
    229,102,73,104,249,233,239,185,190,88,233,188,59,9,172,207,
    234,251,26,89,7,96,109,206,142,120,236,118,60,200,55,190,
    116,93,87,167,41,91,44,147,178,175,134,132,142,120,54,234,
    149,106,76,227,251,254,118,51,51,41,12,183,136,175,142,1
])

keypair = Keypair.from_bytes(key_bytes)
base58_key = base58.b58encode(bytes(keypair)).decode()
public_key = str(keypair.pubkey())

# ✅ Ensure these lines are present:
print("✅ Paste this into your .env:\n")
print(f"WALLET_PRIVATE_KEY={base58_key}")
print(f"WALLET_ADDRESS={public_key}")