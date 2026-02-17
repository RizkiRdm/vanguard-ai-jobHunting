import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# The key must be 32 URL-safe base64-encoded bytes.
SECRET_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(SECRET_KEY.encode())


def encrypt_credential(plain_text: str) -> str:
    """Encrypt sensitive data into Fernet tokens."""
    if not plain_text:
        return plain_text
    return cipher_suite.encrypt(plain_text.encode()).decode()


def decrypt_credential(cipher_text: str) -> str:
    """Decrypting the Fernet token back to the original text."""
    if not cipher_text:
        return cipher_text
    return cipher_suite.decrypt(cipher_text.encode()).decode()


def mask_email(email: str) -> str:
    """Masking PII for API display security."""
    try:
        name, domain = email.split("@")
        return f"{name[:3]}***@{domain}"
    except:
        return email
