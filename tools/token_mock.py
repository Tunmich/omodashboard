import json
import random
import argparse
import string
import logging

# Supported chains
CHAINS = ["Ethereum", "BNB", "Base", "Solana"]

# Solana mock generator
def generate_solana_address():
    return "SoL" + ''.join(random.choices(string.ascii_letters + string.digits, k=30))

# EVM-style mock address
def generate_evm_address(index):
    suffix = str(index).zfill(2)
    return f"0x00{suffix}abc12345678900000000000000000000{suffix}"

# 🚀 Generator function
def generate_mock_tokens(n, output_file):
    tokens = []
    for i in range(n):
        chain = random.choice(CHAINS)
        name = f"MockToken_{i+1}"
        buzz_score = random.randint(50, 100)
        token_price = round(random.uniform(0.0005, 0.006), 6)

        address = generate_solana_address() if chain == "Solana" else generate_evm_address(i+1)

        token = {
            "name": name,
            "chain": chain,
            "address": address,
            "token_price_usd": token_price,
            "buzz_score": buzz_score
        }
        tokens.append(token)

    with open(output_file, "w") as f:
        json.dump(tokens, f, indent=2)

    print(f"✅ Saved {n} mock tokens to {output_file}")

# 📦 CLI wrapper
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mock Token Generator CLI")
    parser.add_argument("-n", "--count", type=int, default=20, help="Number of tokens to generate")
    parser.add_argument("-o", "--output", type=str, default="simulated_tokens.json", help="Output filename")

    args = parser.parse_args()
    generate_mock_tokens(args.count, args.output)