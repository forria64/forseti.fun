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
    print(f"[DEBUG] Checking environment for {var}: {'FOUND' if val else 'NOT FOUND'}")
    if val:
        return val
    val = input(f"{prompt_text}: ").strip()
    print(f"[DEBUG] User input for {var}: {val}")
    return val

def fetch_owned_tokens(principal, api_key):
    url = f"{ODIN_API_BASE}/user/{principal}/tokens"
    headers = {"Authorization": f"Bearer {api_key}"}
    print(f"[DEBUG] Fetching owned tokens from {url} with headers {headers}")
    resp = requests.get(url, headers=headers)
    print(f"[DEBUG] Response status code: {resp.status_code}")
    print(f"[DEBUG] Response content: {resp.content}")
    resp.raise_for_status()
    tokens = resp.json()
    print(f"[DEBUG] Tokens fetched: {tokens}")
    return tokens.get("data", [])  # Only return the list of tokens

def fetch_quote_from_canister():
    print(f"[DEBUG] Fetching quote from canister {FORSETI_CANISTER_ID} on network {DFX_NETWORK}")
    try:
        output = subprocess.check_output([
            "dfx", "canister", "--network", DFX_NETWORK, "call",
            FORSETI_CANISTER_ID, "get_quote"
        ], stderr=subprocess.STDOUT, text=True)
        print(f"[DEBUG] Raw dfx output: {output}")
        match = re.search(r'"(.*)"', output)
        if match:
            quote = match.group(1)
            print(f"[DEBUG] Extracted quote (escaped): {quote}")
            unescaped = bytes(quote, "utf-8").decode("unicode_escape")
            print(f"[DEBUG] Unescaped quote: {unescaped}")
            return unescaped
        else:
            print(f"[DEBUG] No match found in dfx output, returning raw output.")
            return output.strip()
    except Exception as e:
        print(f"[DEBUG] Error fetching quote from canister: {e}")
        return "Forseti is silent today."

def post_comment(token_id, comment, api_key):
    url = f"{ODIN_API_BASE}/token/{token_id}/comment"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"content": comment}
    print(f"[DEBUG] Posting comment to {url} with data {data} and headers {headers}")
    resp = requests.post(url, json=data, headers=headers)
    print(f"[DEBUG] Response status code: {resp.status_code}")
    print(f"[DEBUG] Response content: {resp.content}")
    resp.raise_for_status()
    try:
        result = resp.json()
        print(f"[DEBUG] Comment post result: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG] Error decoding JSON response: {e}")
        return None

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
    print(f"[DEBUG] Writing systemd service to {service_path}")
    with open(service_path, "w") as f:
        f.write(service_content)
    print(f"[DEBUG] Systemd service written.")
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "--now", "odin-bot"], check=True)
    print("[DEBUG] Service enabled and started.")

def main():
    print("[DEBUG] Starting odin-bot main()")
    api_key = get_env_or_prompt("ODIN_API_KEY", "Odin.fun API Key")
    principal = get_env_or_prompt("ODIN_PRINCIPAL", "Odin.fun Principal (Account ID)")

    if len(sys.argv) > 1 and sys.argv[1] == "--install-service":
        if os.geteuid() != 0:
            print("[DEBUG] Not running as root, exiting.")
            print("This command must be run with sudo/root for service installation.")
            sys.exit(1)
        write_systemd_service(api_key, principal)
        return

    while True:
        try:
            print("[DEBUG] Fetching tokens...")
            tokens = fetch_owned_tokens(principal, api_key)
            if not tokens:
                print("[DEBUG] No owned tokens found.")
            else:
                print(f"[DEBUG] {len(tokens)} tokens found.")
                quote = fetch_quote_from_canister()
                print(f"[DEBUG] Quote to post: {quote}")
                for token in tokens:
                    print(f"[DEBUG] Token object: {token}")
                    # Odin.fun API returns each token as {'balance': ..., 'token': {...}}
                    if isinstance(token, dict) and "token" in token and "id" in token["token"]:
                        token_id = token["token"]["id"]
                        print(f"[DEBUG] Extracted token_id: {token_id}")
                        comment = f"{quote}"
                        print(f"[DEBUG] Posting comment to token {token_id}: {comment}")
                        post_comment(token_id, comment, api_key)
                        print("[DEBUG] Posted.")
                    else:
                        print(f"[DEBUG] Skipping token object, could not extract token_id: {token}")
        except Exception as e:
            print("[DEBUG] Error in main loop:", e)
        print("[DEBUG] Sleeping for 2 hours...")
        time.sleep(2 * 60 * 60)  # Sleep for 2 hours

if __name__ == "__main__":
    main()