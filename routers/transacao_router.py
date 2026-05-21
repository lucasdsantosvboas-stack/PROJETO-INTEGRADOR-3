from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/v1/transacoes", tags=["Transações"])

@router.get("/", response_model=list[schemas.TransacaoResponse])
def listar_transacoes(db: Session = Depends(get_db)):
    return db.query(models.Transacao).all()

@router.get("/{transacao_id}", response_model=schemas.TransacaoResponse)
def buscar_transacao(transacao_id: int, db: Session = Depends(get_db)):
    db_transacao = db.query(models.Transacao).filter(models.Transacao.id == transacao_id).first()
    if not db_transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return db_transacao

@router.post("/", response_model=schemas.TransacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_transacao(transacao: schemas.TransacaoCreate, db: Session = Depends(get_db)):
    if transacao.proprietario_id == transacao.cliente_id:
        raise HTTPException(
            status_code=400,
            detail="O proprietário não pode ser o mesmo cliente da transação."
        )
    db_transacao = models.Transacao(**transacao.model_dump())
    db.add(db_transacao)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao

@router.put("/{transacao_id}", response_model=schemas.TransacaoResponse)
def atualizar_transacao(transacao_id: int, transacao: schemas.TransacaoCreate, db: Session = Depends(get_db)):
    db_transacao = db.query(models.Transacao).filter(models.Transacao.id == transacao_id).first()
    if not db_transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    if transacao.proprietario_id == transacao.cliente_id:
        raise HTTPException(status_code=400, detail="O proprietário não pode ser o mesmo cliente da transação.")
    for campo, valor in transacao.model_dump().items():
        setattr(db_transacao, campo, valor)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao

@router.delete("/{transacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_transacao(transacao_id: int, db: Session = Depends(get_db)):
    db_transacao = db.query(models.Transacao).filter(models.Transacao.id == transacao_id).first()
    if not db_transacao:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    db.delete(db_transacao)
    db.commit()
