# utils/wallet_mapper.py

import os
from solders.pubkey import Pubkey
from eth_utils import keccak, to_checksum_address


def phantom_to_evm(phantom_address: str) -> str | None:
    """
    Converts a Phantom (Solana) wallet address to an EVM-compatible address.
    This is a placeholder implementation — replace with actual logic if needed.
    
    Args:
        phantom_address (str): Solana wallet address.
    
    Returns:
        str | None: EVM-compatible address or None if conversion fails.
    """
    try:
        sol_bytes = bytes(Pubkey.from_string(phantom_address))
        hashed = keccak(sol_bytes)[12:]
        return to_checksum_address("0x" + hashed.hex())
    except Exception as e:
        print(f"⚠️ phantom_to_evm failed: {e}")
        return None


def get_safe_evm_wallet(sol_address: str | None = None) -> str | None:
    """
    Safely retrieves an EVM wallet address from a Solana public key.
    If no address is provided, it attempts to load from the SOLANA_WALLET env variable.
    
    Args:
        sol_address (str | None): Optional Solana wallet address.
    
    Returns:
        str | None: EVM-compatible address or None if unavailable or conversion fails.
    """
    try:
        sol = sol_address or os.getenv("SOLANA_WALLET")
        if not sol:
            print("⚠️ Missing Solana address for EVM conversion.")
            return None

        sol_bytes = bytes(Pubkey.from_string(sol))
        hashed = keccak(sol_bytes)[12:]
        return to_checksum_address("0x" + hashed.hex())
    except Exception as e:
        print(f"⚠️ get_safe_evm_wallet failed: {e}")
        return None

