import os
import sys
import time
import requests
import getpass
import subprocess
import re

ODIN_API_BASE = "https://api.odin.fun/v1"
FORSETI_CANISTER_ID = "wnbu2-tyaaa-aaaak-queqa-cai"
DFX_NETWORK = os.environ.get("DFX_NETWORK", "ic")

def get_env_or_prompt(var, prompt_text):
    val = os.environ.get(var)
    if val:
        return val
    return input(f"{prompt_text}: ").strip()

def fetch_owned_tokens(principal, api_key):
    url = f"{ODIN_API_BASE}/user/{principal}/tokens"
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()  # Should be a list of tokens

def fetch_quote_from_canister():
    # Fetch a quote from the Forseti backend canister using dfx, just like x_bot
    try:
        output = subprocess.check_output([
            "dfx", "canister", "--network", DFX_NETWORK, "call",
            FORSETI_CANISTER_ID, "get_quote"
        ], stderr=subprocess.STDOUT, text=True)
        # Extract the quote string using regex (identical to x_bot)
        match = re.search(r'"(.*)"', output)
        if match:
            quote = match.group(1)
            # Unescape any escaped characters
            return bytes(quote, "utf-8").decode("unicode_escape")
        else:
            return output.strip()
    except Exception as e:
        print(f"Error fetching quote from canister: {e}")
        return "Forseti is silent today."

def post_comment(token_id, comment, api_key):
    url = f"{ODIN_API_BASE}/token/{token_id}/comment"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"content": comment}
    resp = requests.post(url, json=data, headers=headers)
    resp.raise_for_status()
    return resp.json()

def write_systemd_service(api_key, principal):
    service_content = f"""[Unit]
Description=Odin.fun Bot Comment Poster
After=network.target

[Service]
Type=simple
Restart=always
User={getpass.getuser()}
WorkingDirectory={os.path.dirname(os.path.abspath(__file__))}
Environment=ODIN_API_KEY={api_key}
Environment=ODIN_PRINCIPAL={principal}
ExecStart={sys.executable} {os.path.abspath(__file__)}

[Install]
WantedBy=multi-user.target
"""
    service_path = "/etc/systemd/system/odin-bot.service"
    with open(service_path, "w") as f:
        f.write(service_content)
    print(f"Systemd service written to {service_path}")
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "--now", "odin-bot"], check=True)
    print("Service enabled and started.")

def main():
    api_key = get_env_or_prompt("ODIN_API_KEY", "Odin.fun API Key")
    principal = get_env_or_prompt("ODIN_PRINCIPAL", "Odin.fun Principal (Account ID)")

    if len(sys.argv) > 1 and sys.argv[1] == "--install-service":
        if os.geteuid() != 0:
            print("This command must be run with sudo/root for service installation.")
            sys.exit(1)
        write_systemd_service(api_key, principal)
        return

    while True:
        try:
            tokens = fetch_owned_tokens(principal, api_key)
            if not tokens:
                print("No owned tokens found.")
            quote = fetch_quote_from_canister()
            for token in tokens:
                comment = f"{quote}"
                print(f"Posting comment to token {token['id']}: {comment}")
                post_comment(token["id"], comment, api_key)
                print("Posted.")
        except Exception as e:
            print("Error:", e)
        time.sleep(2 * 60 * 60)  # Sleep for 2 hours

if __name__ == "__main__":
    main()