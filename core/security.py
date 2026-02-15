import os
import base64
from datetime import datetime, timedelta
from typing import Optional, Union, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# --- PASSWORD HASHING SETUP (BCRYPT) ---
# used for application login passwords (one-way hash)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- AES ENCRYPTION SETUP (FERNET) ---
# used for portal credentials (two-way encryption)
SECRET_KEY_RAW = os.getenv("SECRET_KEY_AES")
SECURITY_SALT = os.getenv("SECURITY_SALT")

# --- JWT CONFIGURATION ---
# strict configuration for modern security standards
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-for-dev-only")
JWT_REFRESH_SECRET_KEY = os.getenv(
    "JWT_REFRESH_SECRET_KEY", "fallback-refresh-secret-for-dev-only"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

if not SECRET_KEY_RAW or not SECURITY_SALT:
    raise RuntimeError(
        "missing SECRET_KEY_AES or SECURITY_SALT in .env file. "
        "security initialization failed."
    )


def generate_fernet_key(secret_phrase: str, salt_phrase: str) -> bytes:
    """derives a secure 32-byte fernet key from environment secrets"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_phrase.encode(),
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_phrase.encode()))
    return key


# initialize the fernet cipher
fernet_key = generate_fernet_key(SECRET_KEY_RAW, SECURITY_SALT)
cipher = Fernet(fernet_key)

# --- PUBLIC API FUNCTIONS (ENCRYPTION & HASHING) ---


def encrypt_data(plain_text: str) -> str:
    """encrypts a string into an aes token for portal credentials"""
    if not plain_text:
        return ""
    return cipher.encrypt(plain_text.encode()).decode()


def decrypt_data(encrypted_text: str) -> str:
    """decrypts an aes token back to plain text for agent usage"""
    if not encrypted_text:
        return ""
    try:
        return cipher.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return "DECRYPTION_ERROR"


def hash_password(password: str) -> str:
    """hashes a plain text password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """verifies a plain password against its stored hash"""
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT FUNCTIONS (NEW IMPLEMENTATION) ---


def create_token(
    data: dict, expires_delta: Optional[timedelta] = None, is_refresh: bool = False
) -> str:
    """
    creates a signed jwt token with standardized claims.
    uses different secrets for access and refresh tokens for isolation.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        if is_refresh:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # mandatory claims for security auditing
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "vanguard-ai-auth",
            "aud": "vanguard-ai-app",
        }
    )

    secret = JWT_REFRESH_SECRET_KEY if is_refresh else JWT_SECRET_KEY
    return jwt.encode(to_encode, secret, algorithm=ALGORITHM)


def decode_token(token: str, is_refresh: bool = False) -> dict:
    """
    decodes and validates a jwt token.
    verifies signature, expiration, and audience.
    """
    secret = JWT_REFRESH_SECRET_KEY if is_refresh else JWT_SECRET_KEY
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[ALGORITHM],
            audience="vanguard-ai-app",
            issuer="vanguard-ai-auth",
        )
        return payload
    except JWTError:
        # returns empty dict to signal invalid/expired token
        return {}
