from setuptools import setup

setup(
    name="memebot_sniper",
    version="1.0.0",
    packages=[
        "modules",
        "strategy",
        "utils"
    ],
    include_package_data=True,
    install_requires=[
        "requests",
        "python-telegram-bot",
        "python-dotenv",
        "solana",            # or solana-py, depending on what you're using
        "streamlit"
    ],
    entry_points={
        "console_scripts": [
            "sniperbot=start_sniper_bot:main"  # if you’ve defined a main() function
        ]
    },
    author="Segun",
    description="Solana meme coin sniper bot",
    license="MIT"
)