# tools/fix_key.py
import logging

def convert_decimal_to_hex(raw):
    try:
        # Remove any leading "0x" and clean whitespace
        raw = raw.lower().replace("0x", "").strip()

        # Convert string of comma-separated decimals into integers
        decimal_list = [int(b.strip()) for b in raw.split(",") if b.strip().isdigit()]
        
        # Build hex string from decimal bytes
        hex_key = "0x" + "".join(format(b, "02x") for b in decimal_list)
        return hex_key
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return None

if __name__ == "__main__":
    print("229,102,73,104,249,233,239,185,190,88,233,188,59,9,172,207,234,251,26,89,7,96,109,206,142,120,236,118,60,200,55,190,116,93,87,167,41,91,44,147,178,175,134,132,142,120,54,234,149,106,76,227,251,254,118,51,51,41,12,183,136,175,142,1")
    print("👉 Example: 229,102,73,104,249,233,...,1\n")

    raw_input_key = input(">> ").strip()

    hex_output = convert_decimal_to_hex(raw_input_key)
    if hex_output:
        print(f"\n✅ HEX Private Key:\n{hex_output}")
        print("📋 Copy this into your .env file as PRIVATE_KEY")
    else:
        print("🚫 Invalid input. Double-check your commas and values.")