import os
from cryptography.fernet import Fernet

# The key should be stored in an environment variable (e.g., Rails-style SECRET_KEY_BASE)
# Generate one with: Fernet.generate_key()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

def encrypt_token(token: str) -> str:
    if not ENCRYPTION_KEY:
        return token # Fallback for dev if no key is set
        
    f = Fernet(ENCRYPTION_KEY.encode())
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    if not ENCRYPTION_KEY or not encrypted_token:
        return encrypted_token
        
    try:
        f = Fernet(ENCRYPTION_KEY.encode())
        return f.decrypt(encrypted_token.encode()).decode()
    except Exception:
        # If decryption fails (e.g. key changed or token was not encrypted), return as is
        return encrypted_token
