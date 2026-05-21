from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from auth import hash_senha, verificar_senha, criar_token

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])

@router.post("/registrar", response_model=dict, status_code=status.HTTP_201_CREATED)
def registrar(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.username == usuario.username).first():
        raise HTTPException(status_code=400, detail="Username já está em uso")
    db.add(models.Usuario(username=usuario.username, senha_hash=hash_senha(usuario.password)))
    db.commit()
    return {"message": "Usuário criado com sucesso"}

@router.post("/login", response_model=schemas.TokenResponse)
def login(dados: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.username == dados.username).first()
    if not usuario or not verificar_senha(dados.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
    if not usuario.ativo:
        raise HTTPException(status_code=403, detail="Usuário inativo")
    token = criar_token({"sub": usuario.username})
    return {"access_token": token, "token_type": "bearer"}
