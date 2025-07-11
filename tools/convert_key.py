# convert_key.py
import json
import logging

from eth_keyfile import decode_keyfile_json
from getpass import getpass
import argparse
import os

def extract_private_key(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "rb") as f:
        keyfile_json = json.load(f)

    password = getpass("🔐 Enter wallet password: ")
    try:
        private_key_bytes = decode_keyfile_json(keyfile_json, password.encode())
        private_key_hex = "0x" + private_key_bytes.hex()
        print(f"\n✅ Extracted Private Key:\n{private_key_hex}\n")
        return private_key_hex
    except Exception as e:
        print(f"❌ Failed to decrypt keyfile: {e}")

def write_to_env(private_key_hex, output_file=".env"):
    with open(output_file, "a") as env_file:
        env_file.write(f"PRIVATE_KEY={private_key_hex}\n")
    print(f"📦 Key saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Ethereum private key from JSON keystore.")
    parser.add_argument("json_file", help="Path to the wallet JSON file")
    parser.add_argument("--env", action="store_true", help="Write the extracted key to .env")

    args = parser.parse_args()
    private_key = extract_private_key(args.json_file)
    if private_key and args.env:
        write_to_env(private_key)