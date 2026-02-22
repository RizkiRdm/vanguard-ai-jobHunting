import os
from datetime import datetime, timedelta, timezone
import hashlib
import bcrypt
from cryptography.fernet import Fernet
from fastapi.concurrency import run_in_threadpool

from dotenv import load_dotenv
from fastapi import HTTPException, status, Request
import httpx
from jose import JWTError, jwt

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "vanguard_ultra_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Section: JWT Security


# --- Password Hashing ---
def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# --- Revisi 2: JWT Logic (Fix Secret Key & Timezone) ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid"
        )


# --- Section: Data Security (Utility Functions) ---


def encrypt_credential(plain_text: str) -> str:
    if not plain_text:
        return plain_text
    return cipher_suite.encrypt(plain_text.encode()).decode()


def decrypt_credential(cipher_text: str) -> str:
    if not cipher_text:
        return cipher_text
    return cipher_suite.decrypt(cipher_text.encode()).decode()


def mask_email(email: str) -> str:
    try:
        name, domain = email.split("@")
        return (
            f"{name[:2]}***{name[-1:]}@{domain}" if len(name) > 3 else f"***@{domain}"
        )
    except Exception:
        return email


class MalwareScanner:
    def __init__(self):
        self.api_key = os.getenv("VIRUSTOTAL_API_KEY")
        self.base_url = "https://www.virustotal.com/api/v3"

    async def verify_file_safety(self, file_path: str):
        if not self.api_key:
            return

        # Revisi: Hitung hash tanpa memblokir event loop
        sha256_hash = await run_in_threadpool(self._get_file_hash, file_path)

        # Revisi: Gunakan timeout dan error handling pada request
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                headers = {"x-apikey": self.api_key}
                response = await client.get(
                    f"{self.base_url}/files/{sha256_hash}", headers=headers
                )

                if response.status_code == 200:
                    stats = (
                        response.json()
                        .get("data", {})
                        .get("attributes", {})
                        .get("last_analysis_stats", {})
                    )
                    # Jika lebih dari 1 engine mendeteksi (menghindari false positive ringan)
                    if stats.get("malicious", 0) > 0:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="File rejected: Security policy violation (Malicious content).",
                        )

                # Logic untuk upload file baru (Opsional - disarankan untuk file sensitif)
                elif response.status_code == 404:
                    pass

            except httpx.HTTPError:
                # Jika API VT down, jangan hentikan proses bisnis (fail-open)
                print("⚠️ VirusTotal API unreachable.")

    def _get_file_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(
                lambda: f.read(8192), b""
            ):  # Buffer 8KB lebih efisien
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
