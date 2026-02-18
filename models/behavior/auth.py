"""
models/behavior/auth.py

Author: Jason Fuller

Password hashing helpers using SALT + PEPPER (models layer).

Responsibilities:
- Generate secure password hashes for storage
- Verify login attempts against stored hashes
- Enforce presence of a server-side PEPPER

Design goals:
- Store a single string in MongoDB for the password field
- Use a per-user random SALT (stored in that string)
- Use a server-side PEPPER from environment variables
- Verify by recomputing hash from (pepper + password) + salt

Stored format:
    pbkdf2$<iterations>$<salt_hex>$<hash_hex>

Security notes:
- SALT is not secret and is stored with the hash
- PEPPER is secret and must never be stored or logged
- Changing PEPPER invalidates all existing passwords

Logging:
- DEBUG: helper lifecycle events (no sensitive data)
- WARN: invalid input or malformed stored hashes
- ERROR: missing PEPPER configuration (abort execution)
"""

# ------------------------------------------------------------------
# Standard library imports
# ------------------------------------------------------------------
import hashlib
import hmac
import os
import secrets

# ------------------------------------------------------------------
# Local application imports
# ------------------------------------------------------------------
from utils.logger import get_logger


logger = get_logger(__name__)


PEPPER = os.getenv("PEPPER")     # from environment
ITERATIONS = 210_000             # safe modern baseline
SALT_BYTES = 16                  # 128-bit salt
DKLEN = 32                       # 256-bit derived key


def _require_pepper() -> str:
    """
    Ensure PEPPER is configured.

    Raises:
        RuntimeError if PEPPER is missing.
    """
    if not PEPPER:
        logger.error("Missing PEPPER environment variable")
        raise RuntimeError("Missing PEPPER env var. Set PEPPER in your .env file.")

    return PEPPER


def hash_password(password: str) -> str:
    """
    Create a salted and peppered password hash.

    Returns:
        A single string: pbkdf2$<iterations>$<salt_hex>$<hash_hex>
    """
    logger.debug("Hashing password")

    pepper = _require_pepper()

    if not password or not isinstance(password, str):
        logger.warn("Invalid password input for hashing")
        raise ValueError("Password must be a non-empty string")

    salt = secrets.token_bytes(SALT_BYTES)
    pw = (pepper + password).encode("utf-8")

    dk = hashlib.pbkdf2_hmac(
        "sha256",
        pw,
        salt,
        ITERATIONS,
        dklen=DKLEN,
    )

    logger.debug("Password hash generated successfully")

    return f"pbkdf2${ITERATIONS}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """
    Verify a login attempt against a stored hash string.

    Verification steps:
    - Parse iterations and salt from stored string
    - Recompute PBKDF2(pepper + password, salt)
    - Compare using constant-time comparison

    Returns:
        True if password matches, False otherwise.
    """
    logger.debug("Verifying password")

    try:
        pepper = _require_pepper()

        algo, iter_str, salt_hex, hash_hex = stored.split("$")
        if algo != "pbkdf2":
            logger.warn("Unsupported password hash algorithm")
            return False

        iterations = int(iter_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)

        pw = (pepper + password).encode("utf-8")
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            pw,
            salt,
            iterations,
            dklen=len(expected),
        )

        return hmac.compare_digest(actual, expected)

    except Exception:
        # Intentionally silent: do not leak failure mode
        logger.warn("Password verification failed")
        return False
