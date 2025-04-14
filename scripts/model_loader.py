#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Generator

def run_dfx_command(command: list) -> str:
    """Run a dfx command and return its stdout. Exit on error."""
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("Command", " ".join(command), "failed with error:")
        print(result.stderr)
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
    print("Checking canister health...")
    command = ["dfx", "canister", "call", canister, "health", "--network", network]
    output = run_dfx_command(command)
    print("Health check output:", output)
    if "Ok" not in output:
        print("Canister health check failed.")
        sys.exit(1)

def set_max_tokens(canister: str, network: str, max_tokens_query: str, max_tokens_update: str) -> None:
    """
    Set the max_tokens_query and max_tokens_update parameters for the canister.
    This function calls the set_max_tokens endpoint on the canister.
    """
    print("Setting max tokens...")
    
    # Use f-string to properly format the argument string
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
    print("set_max_tokens response:", output)


def upload_model(model_file: Path, canister: str, chunksize: int, network: str, tmp_dir: Path) -> None:
    """
    Upload the model file in chunks using the file_upload_chunk endpoint.
    For each chunk, write the Candid argument into a temporary file and call:
       dfx canister call <canister> file_upload_chunk --argument-file <tempfile> --network <network>
    """
    print(f"Uploading model file: {model_file}")
    data = model_file.read_bytes()
    offset = 0
    chunk_num = 1

    prepare_temp_dir(tmp_dir)

    for chunk in generate_chunks(data, chunksize):
        vec_str = chunk_to_vec_str(chunk)
        # Build a Candid literal for the record:
        # (record { filename = "<name>"; chunk = vec { ... }; chunksize = <chunksize>; offset = <offset> })
        arg_str = f'(record {{filename = "{model_file.name}"; chunk = {vec_str}; chunksize = {chunksize}; offset = {offset}}})'
        tmp_file = tmp_dir / f"chunk_{chunk_num}.candid"
        with tmp_file.open("w") as f:
            f.write(arg_str)
        print(f"Uploading chunk {chunk_num}: offset {offset}, size {len(chunk)} bytes")
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
        output = run_dfx_command(command)
        print(f"Chunk {chunk_num} uploaded. Response: {output}")
        offset += len(chunk)
        chunk_num += 1
        tmp_file.unlink()  # Delete the temporary file after use.
        time.sleep(0.1)

    print("Model file upload complete.")

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
    print("Initializing model with arguments from:", tmp_file)
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
    print("Model initialization response:")
    print(output)
    tmp_file.unlink()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Upload a model file and initialize the LLM canister using dfx with arguments from temporary files."
    )
    parser.add_argument(
        "--model-file",
        required=True,
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
    return parser.parse_args()

def main():
    args = parse_args()
    model_path = Path(args.model_file)
    if not model_path.exists():
        print(f"ERROR: Model file {model_path} does not exist!")
        sys.exit(1)

    tmp_dir = Path(args.tmp_dir)
    check_health(args.canister, args.network)
    set_max_tokens(args.canister, args.network, args.max_tokens_query, args.max_tokens_update)
    upload_model(model_path, args.canister, args.chunksize, args.network, tmp_dir)
    initialize_model(args.canister, model_path.name, args.network, tmp_dir)

if __name__ == "__main__":
    main()

