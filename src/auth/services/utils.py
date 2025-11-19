import hashlib
import uuid


class HashPassword:
    """Hash password class."""

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash password."""
        salt = uuid.uuid4().hex
        return hashlib.md5(salt.encode() + password.encode()).hexdigest() + ':' + salt

    @classmethod
    def check_password(cls, hashed_password: str, user_password: str) -> bool:
        """Check password."""
        password, salt, *_ = hashed_password.split(':') + [':']
        return password == hashlib.md5(salt.encode() + user_password.encode()).hexdigest()
