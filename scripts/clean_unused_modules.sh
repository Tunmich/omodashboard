#!/bin/bash
# clean_unused_modules.sh
echo "🧹 Starting unused module scan..."

# 🗂️ Create trash folder if it doesn't exist
mkdir -p trash

# 🧾 Gather all .py modules
find . -type f -name "*.py" > all_py_files.txt

# 🔍 Loop through each module
> unused_modules.txt
while read file; do
    # Skip auto folders
    [[ "$file" =~ "venv" ]] && continue
    [[ "$file" =~ "__init__" ]] && continue

    filename=$(basename "$file")
    module="${filename%.py}"

    # Only check modules with clear names
    if [[ "$module" != "main" && "$module" != "bootstrap" && "$module" != "preflight_checker" ]]; then
        hits=$(grep -r "$module" . | grep -v "$file")
        if [[ -z "$hits" ]]; then
            echo "🗑️ UNUSED: $file → no other module imports or calls '$module'"
            echo "$file" >> unused_modules.txt
        fi
    fi
done < all_py_files.txt

echo ""
echo "⚠️ Scan complete. Modules flagged for review:"
cat unused_modules.txt

echo ""
read -p "❓ Move these files to trash/? [y/N]: " answer
if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
    while read file; do
        mv "$file" "trash/"
        echo "✅ Moved $file to trash/"
    done < unused_modules.txt
    echo "🧤 Cleanup complete. You can restore from trash/ if needed."
else
    echo "🚫 No changes made. Review unused_modules.txt manually."
fi
