import os
import hashlib
import bcrypt
import httpx
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import HTTPException, status, Request
from fastapi.concurrency import run_in_threadpool
from jose import JWTError, jwt

from core.custom_logging import logger
from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

load_dotenv()

# --- Configuration & Encryption Setup ---
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "vanguard_ultra_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# --- Password Hashing (Bcrypt) ---
def get_password_hash(password: str) -> str:
    """Generates a secure hash for a plain text password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# --- Authentication & JWT Logic ---
def create_access_token(data: dict) -> str:
    """Generates a JWT access token with an expiration timestamp."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user_from_cookie(request: Request) -> str:
    """Extracts and validates the user_id from the session cookie."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session payload",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
        )


# --- Data Security & PII Masking ---
def encrypt_credential(plain_text: str) -> str:
    """Encrypts sensitive strings (e.g., API keys) using Fernet."""
    if not plain_text:
        return plain_text
    return cipher_suite.encrypt(plain_text.encode()).decode()


def decrypt_credential(cipher_text: str) -> str:
    """Decrypts Fernet-encrypted strings."""
    if not cipher_text:
        return cipher_text
    return cipher_suite.decrypt(cipher_text.encode()).decode()


def mask_email(email: str) -> str:
    """Masks email addresses to protect PII in logs/UI."""
    if "@" not in email:
        return email
    try:
        name, domain = email.split("@")
        if len(name) > 3:
            return f"{name[:3]}***{name[-1:]}@{domain}"
        return f"***@{domain}"
    except Exception:
        return email


# --- Security Scanning Service ---
class MalwareScanner:
    """
    Service for validating file integrity and safety via VirusTotal API.
    Follows a 'fail-open' policy to ensure business continuity if API is down.
    """

    def __init__(self):
        self.api_key = os.getenv("VIRUSTOTAL_API_KEY")
        self.base_url = "https://www.virustotal.com/api/v3"
        self.log = logger.bind(service="malware_scanner")

    async def verify_file_safety(self, file_path: str):
        """Checks file hash against VirusTotal database."""
        if not self.api_key:
            self.log.warning("vt_scan_skipped", reason="API key missing")
            return

        # Calculate hash in a threadpool to avoid blocking the event loop
        sha256_hash = await run_in_threadpool(self._get_file_hash, file_path)

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                headers = {"x-apikey": self.api_key}
                response = await client.get(
                    f"{self.base_url}/files/{sha256_hash}", headers=headers
                )

                if response.status_code == 200:
                    attributes = response.json().get("data", {}).get("attributes", {})
                    stats = attributes.get("last_analysis_stats", {})

                    # Threshold: File is rejected if at least one engine detects malware
                    if stats.get("malicious", 0) > 0:
                        self.log.error("malicious_file_detected", file_hash=sha256_hash)
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="File rejected: Security policy violation (Malicious content detected).",
                        )

                elif response.status_code == 404:
                    self.log.info(
                        "vt_hash_not_found", detail="New file, assuming clean"
                    )

            except httpx.HTTPError as e:
                # Fail-open: Log the error but do not stop the pipeline
                self.log.warning("vt_api_unreachable", error=str(e))

    def _get_file_hash(self, file_path: str) -> str:
        """Computes SHA256 hash using a buffered approach for memory efficiency."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Use 8KB buffer blocks
            for byte_block in iter(lambda: f.read(8192), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class GoogleAuthService:
    @staticmethod
    async def verify_google_token(token: str) -> dict:
        """
        Verifikasi token ID dari Google Frontend.
        """
        try:
            # Menggunakan run_in_threadpool karena library google-auth bersifat blocking
            id_info = await run_in_threadpool(
                id_token.verify_oauth2_token,
                token,
                requests.Request(),
                GOOGLE_CLIENT_ID,
            )

            if id_info["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise ValueError("Wrong issuer.")

            return {
                "email": id_info["email"],
                "google_id": id_info["sub"],
                "picture": id_info.get("picture"),
            }
        except Exception as e:
            logger.error("google_auth_failed", error=str(e))
            raise HTTPException(status_code=401, detail="Invalid Google Token")
