"""Password hashing and verification service using bcrypt directly.

This service provides:
- Password hashing with bcrypt (12 rounds)
- Password verification
- Automatic salt generation
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with 12 rounds.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password in bcrypt format ($2b$12$...)

    Note:
        bcrypt has a 72-byte limit. Passwords are automatically truncated
        to 72 bytes before hashing.
    """
    # Truncate to 72 bytes (bcrypt limitation)
    password_bytes = password.encode('utf-8')[:72]

    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise

    Note:
        bcrypt has a 72-byte limit. Passwords are automatically truncated
        to 72 bytes before verification.
    """
    # Truncate to 72 bytes (bcrypt limitation)
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(password_bytes, hashed_bytes)
