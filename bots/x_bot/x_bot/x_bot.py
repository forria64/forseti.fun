import os
import sys
import time
import tweepy
import getpass
import subprocess

CANISTER_ID = "wnbu2-tyaaa-aaaak-queqa-cai"

def get_env_or_prompt(var, prompt_text):
    val = os.environ.get(var)
    if not val:
        val = input(f"Enter {prompt_text}: ")
    return val

def get_quote():
    # Use dfx canister call to fetch the quote
    cmd = [
        "dfx", "canister", "--network", "ic", "call", CANISTER_ID, "get_quote"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"dfx error: {result.stderr}")
    out = result.stdout.strip()
    # Example output: '("your quote here")' or '(variant { Ok = "your quote here" })'
    # Try to extract the quoted string
    if '"' in out:
        return out.split('"')[1]
    else:
        raise Exception(f"Unexpected canister output: {out}")

def post_to_twitter(text, api_key, api_secret, access_token, access_secret):
    # Twitter/X limit is 280 characters
    if len(text) > 280:
        text = text[:277] + "..."
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    api = tweepy.API(auth)
    api.update_status(text)

def write_systemd_service(api_key, api_secret, access_token, access_secret):
    service_content = f"""[Unit]
Description=Forseti X Bot Twitter Poster
After=network.target

[Service]
Type=simple
Restart=always
User={getpass.getuser()}
WorkingDirectory={os.path.dirname(os.path.abspath(__file__))}
Environment=TWITTER_API_KEY={api_key}
Environment=TWITTER_API_SECRET={api_secret}
Environment=TWITTER_ACCESS_TOKEN={access_token}
Environment=TWITTER_ACCESS_SECRET={access_secret}
ExecStart={sys.executable} {os.path.abspath(__file__)}

[Install]
WantedBy=multi-user.target
"""
    service_path = "/etc/systemd/system/forseti-x-bot.service"
    with open(service_path, "w") as f:
        f.write(service_content)
    print(f"Systemd service written to {service_path}")
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "--now", "forseti-x-bot"], check=True)
    print("Service enabled and started.")

def main():
    # Get credentials from env or prompt
    api_key = get_env_or_prompt("TWITTER_API_KEY", "Twitter API Key")
    api_secret = get_env_or_prompt("TWITTER_API_SECRET", "Twitter API Secret")
    access_token = get_env_or_prompt("TWITTER_ACCESS_TOKEN", "Twitter Access Token")
    access_secret = get_env_or_prompt("TWITTER_ACCESS_SECRET", "Twitter Access Secret")

    # If called with --install-service, set up systemd and exit
    if len(sys.argv) > 1 and sys.argv[1] == "--install-service":
        if os.geteuid() != 0:
            print("This command must be run with sudo/root for service installation.")
            sys.exit(1)
        write_systemd_service(api_key, api_secret, access_token, access_secret)
        return

    while True:
        try:
            quote = get_quote()
            print(f"Posting quote: {quote}")
            post_to_twitter(quote, api_key, api_secret, access_token, access_secret)
            print("Posted to Twitter.")
        except Exception as e:
            print("Error:", e)
        time.sleep(2 * 60 * 60)  # Sleep for 2 hours

if __name__ == "__main__":
    main()