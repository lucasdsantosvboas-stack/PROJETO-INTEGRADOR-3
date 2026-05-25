from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
import hashlib

router = APIRouter(prefix="/api/v1/corretores", tags=["Corretores"])

# Aceita requisições com ou sem a barra no final
@router.get("")
@router.get("/", response_model=list[schemas.CorretorResponse])
def listar_corretores(db: Session = Depends(get_db)):
    """Lista todos os corretores cadastrados."""
    return db.query(models.Corretor).all()

@router.get("/{corretor_id}", response_model=schemas.CorretorResponse)
def buscar_corretor(corretor_id: int, db: Session = Depends(get_db)):
    """Busca um corretor específico por ID."""
    db_corretor = db.query(models.Corretor).filter(models.Corretor.id == corretor_id).first()
    if not db_corretor:
        raise HTTPException(status_code=404, detail="Corretor não encontrado")
    return db_corretor

# Aceita requisições com ou sem a barra no final
@router.post("")
@router.post("/", response_model=schemas.CorretorResponse, status_code=status.HTTP_201_CREATED)
def criar_corretor(corretor: schemas.CorretorCreate, db: Session = Depends(get_db)):
    """Cria um novo corretor."""
    if db.query(models.Corretor).filter(models.Corretor.email == corretor.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado no sistema")
    if db.query(models.Corretor).filter(models.Corretor.registro_profissional == corretor.registro_profissional).first():
        raise HTTPException(status_code=400, detail="CRECI já cadastrado no sistema")

    hash_senha = hashlib.sha256(corretor.senha.encode()).hexdigest()
    
    db_corretor = models.Corretor(
        nome=corretor.nome,
        email=corretor.email,
        registro_profissional=corretor.registro_profissional,
        hashed_password=hash_senha,
        ativo=True
    )
    
    try:
        db.add(db_corretor)
        db.commit()
        db.refresh(db_corretor)
        return db_corretor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar corretor: {e}")

@router.delete("/{corretor_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_corretor(corretor_id: int, db: Session = Depends(get_db)):
    """Deleta um corretor."""
    db_corretor = db.query(models.Corretor).filter(models.Corretor.id == corretor_id).first()
    if not db_corretor:
        raise HTTPException(status_code=404, detail="Corretor não encontrado")
    db.delete(db_corretor)
    db.commit()