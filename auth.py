# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models
from database import get_db

SECRET_KEY = "erp-imobiliaria-secret-key-2024"
ALGORITHM  = "HS256"
TOKEN_EXPIRE_HOURS = 8

oauth2_scheme  = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha: str, hash: str) -> bool:
    return hashlib.sha256(senha.encode()).hexdigest() == hash

def criar_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise exc
    except JWTError:
        raise exc
    usuario = db.query(models.Usuario).filter(models.Usuario.username == username).first()
    if not usuario or not usuario.ativo:
        raise exc
    return usuario
