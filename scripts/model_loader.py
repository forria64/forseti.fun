#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Generator
import urllib.request
import pygame
from threading import Thread
from colorama import Fore, Style, init as colorama_init

# ASCII Art Banner
ASCII_ART = r"""
 ╔═══╗╔═══╗╔═══╗╔═══╗╔═══╗╔════╗╔══╗
 ║╔══╝║╔═╗║║╔═╗║║╔═╗║║╔══╝║╔╗╔╗║╚╣╠╝
 ║╚══╗║║ ║║║╚═╝║║╚══╗║╚══╗╚╝║║╚╝ ║║ 
 ║╔══╝║║ ║║║╔╗╔╝╚══╗║║╔══╝  ║║   ║║ 
╔╝╚╗  ║╚═╝║║║║╚╗║╚═╝║║╚══╗ ╔╝╚╗ ╔╣╠╗
╚══╝  ╚═══╝╚╝╚═╝╚═══╝╚═══╝ ╚══╝ ╚══╝
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~v3.0.0
LOADING MODEL...
"""

def play_chiptune_loop(wav_path: str):
    pygame.mixer.init()
    pygame.mixer.music.load(wav_path)
    pygame.mixer.music.play(-1)  # Loop forever
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def run_dfx_command(command: list) -> str:
    """Run a dfx command and return its stdout. Exit on error."""
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(Fore.RED + "Command", " ".join(command), "failed with error:" + Style.RESET_ALL)
        print(Fore.RED + result.stderr + Style.RESET_ALL)
        sys.exit(1)
    return result.stdout.strip()

def chunk_to_vec_str(chunk: bytes) -> str:
    """
    Convert a bytes object to a string representing a vector of nat8.
    In Candid syntax, vector elements are separated by semicolons.
    Example: "vec { 65;66;67 }"
    """
    return "vec {" + ";".join(str(b) for b in chunk) + "}"

def generate_chunks(data: bytes, chunksize: int) -> Generator[bytes, None, None]:
    """Yield successive chunks from data."""
    for i in range(0, len(data), chunksize):
        yield data[i:i+chunksize]

def prepare_temp_dir(directory: Path) -> None:
    """Ensure the temporary directory exists and is empty."""
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)

def check_health(canister: str, network: str) -> None:
    """Call the health endpoint to ensure the canister is live."""
    print(Fore.CYAN + "Checking canister health..." + Style.RESET_ALL)
    command = ["dfx", "canister", "call", canister, "health", "--network", network]
    output = run_dfx_command(command)
    print(Fore.GREEN + "Health check output:" + Style.RESET_ALL, Fore.YELLOW + output + Style.RESET_ALL)
    if "Ok" not in output:
        print(Fore.RED + "Canister health check failed." + Style.RESET_ALL)
        sys.exit(1)

def set_max_tokens(canister: str, network: str, max_tokens_query: str, max_tokens_update: str) -> None:
    """
    Set the max_tokens_query and max_tokens_update parameters for the canister.
    This function calls the set_max_tokens endpoint on the canister.
    """
    print(Fore.CYAN + "Setting max tokens..." + Style.RESET_ALL)
    arg_str = f"(record {{ max_tokens_query = {max_tokens_query} : nat64; max_tokens_update = {max_tokens_update} : nat64 }})"
    command = [
        "dfx",
        "canister",
        "call",
        canister,
        "set_max_tokens",
        arg_str,
        "--network",
        network
    ]
    output = run_dfx_command(command)
    print(Fore.GREEN + "set_max_tokens response:" + Style.RESET_ALL, Fore.YELLOW + output + Style.RESET_ALL)

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█'):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{Fore.MAGENTA}{prefix} |{bar}| {percent}% {suffix}{Style.RESET_ALL}', end='\r')
    if iteration == total:
        print()  # Newline on complete

def upload_model(model_file: Path, canister: str, chunksize: int, network: str, tmp_dir: Path) -> None:
    """
    Upload the model file in chunks using the file_upload_chunk endpoint.
    If interrupted (e.g., by keyring/DFX errors), pause and resume from the last successful chunk.
    """
    print(Fore.CYAN + f"Uploading model file: {model_file}" + Style.RESET_ALL)
    data = model_file.read_bytes()
    total_chunks = (len(data) + chunksize - 1) // chunksize
    offset = 0
    chunk_num = 1

    prepare_temp_dir(tmp_dir)

    # Progress tracking file
    progress_file = tmp_dir / ".progress"
    last_uploaded = 0
    if progress_file.exists():
        try:
            last_uploaded = int(progress_file.read_text().strip())
            print(Fore.YELLOW + f"Resuming from chunk {last_uploaded + 1}..." + Style.RESET_ALL)
        except Exception:
            last_uploaded = 0

    for chunk in generate_chunks(data, chunksize):
        if chunk_num <= last_uploaded:
            offset += len(chunk)
            chunk_num += 1
            continue

        vec_str = chunk_to_vec_str(chunk)
        arg_str = f'(record {{filename = "{model_file.name}"; chunk = {vec_str}; chunksize = {chunksize}; offset = {offset}}})'
        tmp_file = tmp_dir / f"chunk_{chunk_num}.candid"
        with tmp_file.open("w") as f:
            f.write(arg_str)
        command = [
            "dfx",
            "canister",
            "call",
            canister,
            "file_upload_chunk",
            "--argument-file",
            str(tmp_file),
            "--network",
            network,
        ]
        while True:
            try:
                run_dfx_command(command)
                # Mark this chunk as uploaded
                progress_file.write_text(str(chunk_num))
                break
            except SystemExit as e:
                print(Fore.RED + f"\nDFX/keyring error detected. Please restart your keyring/DFX, then press Enter to retry chunk {chunk_num}..." + Style.RESET_ALL)
                input()
                print(Fore.YELLOW + "Retrying..." + Style.RESET_ALL)
        offset += len(chunk)
        print_progress_bar(chunk_num, total_chunks, prefix='Progress', suffix='Complete', length=40)
        chunk_num += 1
        tmp_file.unlink()
        time.sleep(0.1)

    if progress_file.exists():
        progress_file.unlink()
    print(Fore.GREEN + "Model file upload complete." + Style.RESET_ALL)

def initialize_model(canister: str, model_filename: str, network: str, tmp_dir: Path) -> None:
    """
    Initialize the model by calling the load_model endpoint.
    This function writes a Candid literal to a temporary file and uses --argument-file.
    The canister is expected to receive the arguments as a vector with a flag and the filename.
    For example: (record { args = vec {"--model"; "my_model.gguf"} })
    """
    arg_str = f'(record {{args = vec {{"--model"; "{model_filename}"}}}})'
    tmp_file = tmp_dir / "init_model.candid"
    with tmp_file.open("w") as f:
        f.write(arg_str)
    print(Fore.CYAN + "Initializing model with arguments from:" + Style.RESET_ALL, Fore.YELLOW + str(tmp_file) + Style.RESET_ALL)
    command = [
        "dfx",
        "canister",
        "call",
        canister,
        "load_model",
        "--argument-file",
        str(tmp_file),
        "--network",
        network,
    ]
    output = run_dfx_command(command)
    print(Fore.GREEN + "Model initialization response:" + Style.RESET_ALL)
    print(Fore.YELLOW + output + Style.RESET_ALL)
    tmp_file.unlink()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Upload a model file and initialize the LLM canister using dfx with arguments from temporary files."
    )
    parser.add_argument(
        "--model-file",
        default="models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        help="Path to the model file (e.g. /models/my_model.gguf)",
    )
    parser.add_argument(
        "--canister",
        default="llama_cpp_canister",
        help="Name of the LLM canister as defined in dfx.json (default: llama_cpp_canister)",
    )
    parser.add_argument(
        "--network",
        default="local",
        help="Network to use (e.g. local or ic)",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=2000000,
        help="Chunk size in bytes for upload (default: 2000000)",
    )
    parser.add_argument(
        "--tmp-dir",
        type=str,
        default="./tmp/chunks",
        help="Temporary directory to store argument files (default: ./tmp/chunks)",
    )
    parser.add_argument(
        "--max_tokens_query",
        type=str,
        default="3",
        help="max_tokens_query",
    )
    parser.add_argument(
        "--max_tokens_update",
        type=str,
        default="3",
        help="max_tokens_update",
    )
    parser.add_argument(
        "--chiptune",
        type=str,
        default="scripts/chiptune.wav",
        help="Path to chiptune wav file to play during upload (default: chiptune.wav)",
    )
    return parser.parse_args()

def download_model_if_missing(model_path: Path, url: str):
    if model_path.exists():
        return
    print(Fore.CYAN + f"Model file {model_path} not found. Downloading from {url}..." + Style.RESET_ALL)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url) as response, open(model_path, 'wb') as out_file:
            total_length = response.length or int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if total_length:
                    percent = 100 * downloaded // total_length
                    print(f"\r{Fore.MAGENTA}Downloading: {percent}%{Style.RESET_ALL}", end='')
        print(f"\n{Fore.GREEN}Download complete.{Style.RESET_ALL}")
    except Exception as e:
        print(Fore.RED + f"Failed to download model: {e}" + Style.RESET_ALL)
        sys.exit(1)

def main():
    colorama_init(autoreset=True)
    print(Fore.YELLOW + ASCII_ART + Style.RESET_ALL)
    args = parse_args()
    model_path = Path(args.model_file)
    # Download model if missing
    download_model_if_missing(
        model_path,
        "https://huggingface.co/unsloth/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
    )
    if not model_path.exists():
        print(Fore.RED + f"ERROR: Model file {model_path} does not exist!" + Style.RESET_ALL)
        sys.exit(1)

    # Start chiptune in a background thread
    chiptune_thread = Thread(target=play_chiptune_loop, args=(args.chiptune,), daemon=True)
    chiptune_thread.start()

    tmp_dir = Path(args.tmp_dir)
    check_health(args.canister, args.network)
    set_max_tokens(args.canister, args.network, args.max_tokens_query, args.max_tokens_update)
    upload_model(model_path, args.canister, args.chunksize, args.network, tmp_dir)
    initialize_model(args.canister, model_path.name, args.network, tmp_dir)

    # Stop music after script finishes
    pygame.mixer.music.stop()

if __name__ == "__main__":
    main()