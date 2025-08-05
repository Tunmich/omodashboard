# create_wrappers.py
wrappers = {
    "intel_engine.py": "core.intel_engine",
    "intel_patrol.py": "core.intel_patrol",
    "intel_listener.py": "core.intel_listener",
    "health_check.py": "core.health",
    "main.py": "core.main",
    "start_sniper_bot.py": "core.start_sniper_bot"
}

for filename, module_path in wrappers.items():
    with open(filename, "w") as f:
        f.write(f"""# Auto-generated wrapper for {module_path}
import runpy

if __name__ == "__main__":
    runpy.run_module("{module_path}", run_name="__main__")
""")

print("✅ Wrappers generated.")
