import asyncio
from datetime import datetime,timedelta,timezone
import jwt 
from pwdlib import PasswordHash
from config import settings
passwordhash=PasswordHash.recommended()

async def password_hash(password:str)->str:
    return await asyncio.to_thread(passwordhash.hash, password)

async def verify_password(password:str,hashed:str)->bool:
    return await asyncio.to_thread(passwordhash.verify, password, hashed)


async def create_access_token(subject:str,expires_delta:timedelta| None=None)->str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    # Raises jwt.InvalidTokenError on bad signature or expiry
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
