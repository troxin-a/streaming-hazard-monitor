import hashlib
import secrets

API_KEY_BYTES = 32


def generate_api_key() -> str:
    """Generate a device api key."""
    return secrets.token_urlsafe(API_KEY_BYTES)


def hash_api_key(key: str) -> str:
    """Hash a device api key for storage and lookup."""
    return hashlib.sha256(key.encode()).hexdigest()
