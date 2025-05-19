# Odin.fun Bot

A bot that posts comments to all tokens you own on odin.fun every 2 hours.

## Installation

You can install and run the bot directly from GitHub using pipx:

```sh
pipx install git+https://github.com/forria64/forseti.fun.git#subdirectory=bots/odin_bot
```

This will install the `odin-bot` command globally.

## Usage

Run once:

```sh
odin-bot
```

Install as a systemd service:

```sh
sudo odin-bot --install-service
```

Set your credentials as environment variables for automation:

```sh
export ODIN_API_KEY=your_api_key
export ODIN_PRINCIPAL=your_principal
odin-bot
```

## Configuration

- The bot fetches comments from your backend at `$ODIN_BOT_COMMENT_API` (default: `http://localhost:8000/api/comment`).
- Posts to all tokens you own every 2 hours.