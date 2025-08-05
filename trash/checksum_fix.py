import os

def fix_checksum_calls(root_dir="."):
    fixed_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".py"):
                path = os.path.join(dirpath, fname)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        contents = f.read()
                    if "to_checksum_address" in contents:
                        contents = contents.replace("to_checksum_address", "to_checksum_address")
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(contents)
                        fixed_files.append(path)
                except Exception as e:
                    print(f"⚠️ Error processing {path}: {e}")

    if fixed_files:
        print("\n✅ Replaced calls in the following files:")
        for f in fixed_files:
            print(f"  • {f}")
    else:
        print("📂 No occurrences of 'to_checksum_address' were found.")

if __name__ == "__main__":
    fix_checksum_calls()
