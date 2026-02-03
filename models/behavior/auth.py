"""
models/auth.py

Author: Jason Fuller
Date: 2026-01-25

Simple SALT + PEPPER password hashing helpers for an MVC app (models layer).

Design goals:
- Store ONE string in MongoDB for the password field.
- Use a per-user random SALT (stored in that string).
- Use a server-side PEPPER from .env (never stored in the DB).
- Verify by recomputing the hash from (pepper + password) + salt.

Format stored in DB:
    pbkdf2$<iterations>$<salt_hex>$<hash_hex>

Notes:
- The salt is NOT secret and will be visible in the DB (this is normal).
- The pepper IS secret and must never be stored in the DB.
- If PEPPER changes, all passwords become invalid (treat it like a key).
"""

import os
import hashlib
import hmac
import secrets

PEPPER = os.getenv("PEPPER")  # from .env
ITERATIONS = 210_000          # safe modern baseline
SALT_BYTES = 16               # 128-bit salt
DKLEN = 32                    # 256-bit derived key


def _require_pepper() -> str:
    """Fail fast if PEPPER isn't loaded correctly."""
    if not PEPPER:
        raise RuntimeError("Missing PEPPER env var. Set PEPPER in your .env file.")
    return PEPPER


def hash_password(password: str) -> str:
    """
    Create a salted+peppered password hash to store in database.

    Returns:
        A single string: pbkdf2$<iterations>$<salt_hex>$<hash_hex>
    """
    pepper = _require_pepper()

    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")

    salt = secrets.token_bytes(SALT_BYTES)
    pw = (pepper + password).encode("utf-8")

    dk = hashlib.pbkdf2_hmac("sha256", pw, salt, ITERATIONS, dklen=DKLEN)

    return f"pbkdf2${ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """
    Verify a login attempt against the stored hash string.

    How it works:
    - Reads iterations + salt from the stored string
    - Recomputes PBKDF2(pepper + password, salt, iterations)
    - Compares using constant-time compare
    """
    try:
        pepper = _require_pepper()

        algo, iter_str, salt_hex, hash_hex = stored.split("$")
        if algo != "pbkdf2":
            return False

        iterations = int(iter_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)

        pw = (pepper + password).encode("utf-8")
        actual = hashlib.pbkdf2_hmac("sha256", pw, salt, iterations, dklen=len(expected))

        return hmac.compare_digest(actual, expected)
    except Exception:
        # Don't leak whether it failed due to format or wrong password.
        return False
