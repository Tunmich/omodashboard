import ctypes

try:
    ctypes.CDLL("libssl-3-x64.dll")
    print("✅ DLL loaded successfully!")
except Exception as e:
    print("❌ Error loading DLL:", e)
