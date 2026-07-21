#!/usr/bin/env python3
"""
TEKOSECURE — CLI to manage encrypted Mikrotik secrets.

Usage:
    # 1) Generate a new master key (run once, then paste into backend/.env)
    python3 scripts/encrypt_mikrotik_secret.py --generate-key

    # 2) Encrypt a password (paste result into MIKROTIK_PASSWORD_ENC)
    python3 scripts/encrypt_mikrotik_secret.py --encrypt "MyNewMikrotikPassword"

    # 3) Decrypt back (sanity check)
    python3 scripts/encrypt_mikrotik_secret.py --decrypt "gAAAAAB..."

    # 4) Verify current .env round-trips correctly
    python3 scripts/encrypt_mikrotik_secret.py --check

The master key must be provided via TEKOSECURE_MASTER_KEY environment var
(or a --key argument). Copy backend/.env variables before running --encrypt / --decrypt.
"""

import argparse
import os
import sys
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load /app/backend/.env if present
load_dotenv(Path(__file__).resolve().parent.parent / "backend" / ".env")


def cmd_generate():
    key = Fernet.generate_key().decode()
    print("New master key (copy into backend/.env as TEKOSECURE_MASTER_KEY):\n")
    print(key)
    print("\nRemember: rotating the master key invalidates all existing encrypted blobs.")


def _get_fernet(key_arg: str | None) -> Fernet:
    key = key_arg or os.environ.get("TEKOSECURE_MASTER_KEY")
    if not key:
        sys.exit("ERROR: TEKOSECURE_MASTER_KEY not set. Pass --key or export it.")
    try:
        return Fernet(key.encode())
    except Exception as exc:
        sys.exit(f"ERROR: invalid Fernet key: {exc}")


def cmd_encrypt(text: str, key_arg: str | None):
    f = _get_fernet(key_arg)
    blob = f.encrypt(text.encode()).decode()
    print("Encrypted blob (copy into backend/.env as MIKROTIK_PASSWORD_ENC):\n")
    print(blob)


def cmd_decrypt(blob: str, key_arg: str | None):
    f = _get_fernet(key_arg)
    try:
        plain = f.decrypt(blob.encode()).decode()
    except Exception as exc:
        sys.exit(f"ERROR: decrypt failed: {exc}")
    print(plain)


def cmd_check():
    key = os.environ.get("TEKOSECURE_MASTER_KEY")
    blob = os.environ.get("MIKROTIK_PASSWORD_ENC")
    if not key or not blob:
        sys.exit("ERROR: TEKOSECURE_MASTER_KEY or MIKROTIK_PASSWORD_ENC missing in .env")
    f = Fernet(key.encode())
    try:
        pwd = f.decrypt(blob.encode()).decode()
    except Exception as exc:
        sys.exit(f"ERROR: decrypt failed: {exc}")
    print(f"OK — decrypted length: {len(pwd)} chars, first char: {pwd[0]!r}")


def main():
    p = argparse.ArgumentParser(description="Manage encrypted Mikrotik secrets")
    p.add_argument("--generate-key", action="store_true")
    p.add_argument("--encrypt", metavar="PLAINTEXT")
    p.add_argument("--decrypt", metavar="BLOB")
    p.add_argument("--check", action="store_true")
    p.add_argument("--key", help="Override MASTER key (Fernet base64)")
    args = p.parse_args()

    if args.generate_key:
        cmd_generate()
    elif args.encrypt:
        cmd_encrypt(args.encrypt, args.key)
    elif args.decrypt:
        cmd_decrypt(args.decrypt, args.key)
    elif args.check:
        cmd_check()
    else:
        p.print_help()


if __name__ == "__main__":
    main()
