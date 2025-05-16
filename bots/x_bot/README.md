``` 
███████╗ ██████╗ ██████╗ ███████╗███████╗████████╗██╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝╚══██╔══╝██║
█████╗  ██║   ██║██████╔╝███████╗█████╗     ██║   ██║
██╔══╝  ██║   ██║██╔══██╗╚════██║██╔══╝     ██║   ██║
██║     ╚██████╔╝██║  ██║███████║███████╗   ██║   ██║
╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚═╝
██╗  ██╗    ██████╗  ██████╗ ████████╗
╚██╗██╔╝    ██╔══██╗██╔═══██╗╚══██╔══╝
 ╚███╔╝     ██████╔╝██║   ██║   ██║   
 ██╔██╗     ██╔══██╗██║   ██║   ██║   
██╔╝ ██╗    ██████╔╝╚██████╔╝   ██║   
╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝   
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~v1.0.0
```

A Python bot that fetches mythic quotes from the Forseti IC canister and posts them to Twitter/X on a schedule.

## Features

- Fetches quotes from the Internet Computer Forseti canister using the public API.
- Posts quotes to Twitter/X using your credentials.
- Can be run as a CLI tool or installed as a persistent systemd service (posts every 2 hours).
- Prompts for Twitter credentials if not set as environment variables.
- Supports cycling through a list of topics.

## Requirements

- Python 3.8+
- [pipx](https://pipx.pypa.io/)
- [ic-py](https://github.com/rocklabs-io/ic-py) (installed automatically)
- [tweepy](https://www.tweepy.org/) (installed automatically)

## Installation

You can install and run the bot directly from GitHub using pipx:

```sh
pipx install git+https://github.com/forria64/forseti.fun.git#subdirectory=bots/x_bot
```

This will install the `forseti-x-bot` command globally.

## Usage

### Run Once from the Command Line

You can run the bot directly (it will post a quote every 2 hours):

```sh
forseti-x-bot
```

- The bot will prompt you for your Twitter API credentials if they are not set as environment variables.
- To set credentials as environment variables (recommended for automation):

  ```sh
  export TWITTER_API_KEY=your_key
  export TWITTER_API_SECRET=your_secret
  export TWITTER_ACCESS_TOKEN=your_token
  export TWITTER_ACCESS_SECRET=your_access_secret
  forseti-x-bot
  ```

### Install as a Systemd Service

To run the bot as a persistent background service (posts every 2 hours):

```sh
sudo forseti-x-bot --install-service
```

- You will be prompted for your Twitter credentials if they are not set.
- The service will be created at `/etc/systemd/system/forseti-x-bot.service` and started automatically.
- To check the status:

  ```sh
  systemctl status forseti-x-bot
  ```

- To view logs:

  ```sh
  journalctl -u forseti-x-bot -f
  ```

- To stop or disable the service:

  ```sh
  sudo systemctl stop forseti-x-bot
  sudo systemctl disable forseti-x-bot
  ```

## Customization

- Edit the `TOPICS` list in `x_bot.py` to change or add topics for the quotes.
- The bot cycles through topics in order, posting a new quote every 2 hours.

## Security Notes

- When installing as a service, your Twitter credentials are stored in the systemd unit file as environment variables. For higher security, consider using a secrets manager or systemd environment file.

## Development

Clone the repo and install in editable mode:

```sh
git clone https://github.com/forria64/forseti.fun.git
cd forseti.fun/src/forsetidotfun_backend/bots/x_bot
pipx install --editable .
```

## License

MIT

---

**Repository:**  
https://github.com/forria64/forseti.fun/tree/main/bots/x_bot