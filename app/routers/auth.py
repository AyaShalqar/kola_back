from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
from datetime import datetime, timezone
from app.core.deps import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.auth import RegisterIn, LoginIn, TokenPair, RefreshIn, LogoutIn
from app.models.user import User, RefreshToken

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter((User.email == payload.email) | (User.username == payload.username)).first():
        raise HTTPException(status_code=400, detail="Email or username already in use")
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered"}

@router.post("/login", response_model=TokenPair)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(sub=user.email)
    refresh, jti, exp = create_refresh_token(sub=user.email)

    db_token = RefreshToken(jti=jti, user_id=user.id, expires_at=exp)
    db.add(db_token)
    db.commit()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshIn, db: Session = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
        email = data.get("sub")
        jti = data.get("jti")
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    db_rt = db.query(RefreshToken).filter(RefreshToken.jti == jti, RefreshToken.user_id == user.id).first()
    if not db_rt or db_rt.revoked:
        raise HTTPException(status_code=401, detail="Refresh token revoked or not found")
    
    # Проверка истечения токена
    if db_rt.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Ротация refresh: старый помечаем revoked, выдаём новый
    db_rt.revoked = True

    new_access = create_access_token(sub=user.email)
    new_refresh, new_jti, new_exp = create_refresh_token(sub=user.email)
    db.add(RefreshToken(jti=new_jti, user_id=user.id, expires_at=new_exp))
    db.commit()

    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

@router.post("/logout")
def logout(payload: LogoutIn, db: Session = Depends(get_db)):
    # ревок конкретного refresh токена
    try:
        data = decode_token(payload.refresh_token)
        jti = data.get("jti")
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    db_rt = db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
    if not db_rt:
        # idempotent
        return {"message": "Logged out"}
    db_rt.revoked = True
    db.commit()
    return {"message": "Logged out"}
