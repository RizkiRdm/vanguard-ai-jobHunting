import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- PASSWORD HASHING SETUP (BCRYPT) ---
# Used for application login passwords (One-way hash)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- AES ENCRYPTION SETUP (FERNET) ---
# Used for portal credentials (Two-way encryption)
SECRET_KEY_RAW = os.getenv("SECRET_KEY_AES")
SECURITY_SALT = os.getenv("SECURITY_SALT")

if not SECRET_KEY_RAW or not SECURITY_SALT:
    raise RuntimeError(
        "Missing SECRET_KEY_AES or SECURITY_SALT in .env file. "
        "Security initialization failed."
    )


def generate_fernet_key(secret_phrase: str, salt_phrase: str) -> bytes:
    """
    Derives a secure 32-byte Fernet key from environment secrets.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_phrase.encode(),
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_phrase.encode()))
    return key


# Initialize the Fernet cipher
fernet_key = generate_fernet_key(SECRET_KEY_RAW, SECURITY_SALT)
cipher = Fernet(fernet_key)

# --- PUBLIC API FUNCTIONS ---


def encrypt_data(plain_text: str) -> str:
    """
    Encrypts a string into an AES token.
    Ideal for storing portal passwords.
    """
    if not plain_text:
        return ""
    return cipher.encrypt(plain_text.encode()).decode()


def decrypt_data(encrypted_text: str) -> str:
    """
    Decrypts an AES token back to plain text.
    Used by the automation agent to retrieve portal passwords.
    """
    if not encrypted_text:
        return ""
    try:
        return cipher.decrypt(encrypted_text.encode()).decode()
    except Exception:
        # In case of invalid key or corrupted data
        return "DECRYPTION_ERROR"


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using BCrypt.
    For application user authentication only.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against its stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)
