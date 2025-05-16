from setuptools import setup, find_packages

setup(
    name="forseti-x-bot",
    version="1.0.0",
    description="Forseti Twitter bot for posting quotes from the IC",
    author="forria",
    author_email="forria@forria64.space",
    packages=find_packages(),
    install_requires=[
        "tweepy",
        "ic-py",
    ],
    entry_points={
        "console_scripts": [
            "forseti-x-bot = x_bot.x_bot:main",
        ],
    },
    python_requires=">=3.8",
)