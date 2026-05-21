from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/v1/transacoes", tags=["Transações"])

@router.post("/", response_model=schemas.TransacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_transacao(transacao: schemas.TransacaoCreate, db: Session = Depends(get_db)):
    # Validação de Negócio: Proprietário não pode ser o Comprador
    if transacao.proprietario_id == transacao.cliente_id:
        raise HTTPException(
            status_code=400, 
            detail="O proprietário não pode ser o mesmo cliente da transação (comprador/locatário)."
        )
        
    db_transacao = models.Transacao(**transacao.model_dump())
    db.add(db_transacao)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao

@router.get("/", response_model=list[schemas.TransacaoResponse])
def listar_transacoes(db: Session = Depends(get_db)):
    return db.query(models.Transacao).all()