import os
from datetime import datetime, timedelta
from typing import Optional, Any, Union
from jose import jwt

# Security Configuration
_DEFAULT_DEV_KEY = "dev_secret_key_change_me_in_production"
SECRET_KEY = os.getenv("SECRET_KEY", _DEFAULT_DEV_KEY)

# Refuse to start with insecure default key in any production-like environment
_is_production = any(os.getenv(v) for v in ("RAILWAY_ENVIRONMENT", "VERCEL_ENV", "PRODUCTION"))
if _is_production and SECRET_KEY == _DEFAULT_DEV_KEY:
    raise RuntimeError(
        "FATAL: SECRET_KEY env var is not set. "
        "Generate one with: openssl rand -hex 32"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against its hash using bcrypt."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Generates a bcrypt hash for a password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None
