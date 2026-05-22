from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from auth import hash_senha

router = APIRouter(prefix="/api/v1/corretores", tags=["Corretores & Acesso"])

@router.post("/", response_model=schemas.CorretorResponse, status_code=status.HTTP_201_CREATED)
def registrar_corretor(corretor: schemas.CorretorCreate, db: Session = Depends(get_db)):
    # 1. Verifica se o email ou CRECI já existem
    existe_email = db.query(models.Corretor).filter(models.Corretor.email == corretor.email).first()
    if existe_email:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
        
    # 2. Separa a senha do resto dos dados
    dados_corretor = corretor.model_dump()
    senha_pura = dados_corretor.pop("senha") # Remove a senha do dicionário
    
    # 3. Cria o modelo com a senha hasheada
    db_corretor = models.Corretor(
        **dados_corretor,
        hashed_password=hash_senha(senha_pura)
    )
    
    db.add(db_corretor)
    db.commit()
    db.refresh(db_corretor)
    
    return db_corretor