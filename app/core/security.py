from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from uuid import uuid4
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def _now_utc():
    return datetime.now(timezone.utc)

def create_access_token(sub: str) -> str:
    exp = _now_utc() + timedelta(minutes=settings.ACCESS_EXPIRE_MIN)
    payload = {"sub": sub, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def create_refresh_token(sub: str) -> tuple[str, str, datetime]:
    # генерим jti для ротации/ревока
    jti = str(uuid4())
    exp = _now_utc() + timedelta(days=settings.REFRESH_EXPIRE_DAYS)
    payload = {"sub": sub, "exp": exp, "jti": jti}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token, jti, exp

def decode_token(token: str) -> dict:
    try:
        # ⚙️ очистка токена на случай, если в нём есть "Bearer " или пробелы
        token = token.replace("Bearer", "").replace("bearer", "").strip()
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")
