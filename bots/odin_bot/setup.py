from setuptools import setup, find_packages

setup(
    name="odin-bot",
    version="1.0.0",
    description="Odin.fun bot for posting comments to owned tokens",
    author="forria",
    author_email="forria@forria64.space",
    packages=["odin_bot"],
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "odin-bot = odin_bot.odin_bot:main",
        ],
    },
    python_requires=">=3.8",
)