from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from domain import StatusPagamento

router = APIRouter(prefix="/api/v1/parcelas", tags=["Financeiro"])

@router.get("/", response_model=list[schemas.PagamentoParcelaResponse])
def listar_parcelas(db: Session = Depends(get_db)):
    return db.query(models.PagamentoParcela).all()

@router.get("/{parcela_id}", response_model=schemas.PagamentoParcelaResponse)
def buscar_parcela(parcela_id: int, db: Session = Depends(get_db)):
    db_parcela = db.query(models.PagamentoParcela).filter(models.PagamentoParcela.id == parcela_id).first()
    if not db_parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    return db_parcela

@router.post("/", response_model=schemas.PagamentoParcelaResponse, status_code=status.HTTP_201_CREATED)
def criar_parcela(parcela: schemas.PagamentoParcelaCreate, db: Session = Depends(get_db)):
    db_parcela = models.PagamentoParcela(**parcela.model_dump())
    db.add(db_parcela)
    db.commit()
    db.refresh(db_parcela)
    return db_parcela

@router.put("/{parcela_id}", response_model=schemas.PagamentoParcelaResponse)
def atualizar_parcela(parcela_id: int, parcela: schemas.PagamentoParcelaCreate, db: Session = Depends(get_db)):
    db_parcela = db.query(models.PagamentoParcela).filter(models.PagamentoParcela.id == parcela_id).first()
    if not db_parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    for campo, valor in parcela.model_dump().items():
        setattr(db_parcela, campo, valor)
    db.commit()
    db.refresh(db_parcela)
    return db_parcela

@router.patch("/{parcela_id}/pagar", response_model=schemas.PagamentoParcelaResponse)
def dar_baixa_parcela(parcela_id: int, baixa: schemas.PagamentoBaixa, db: Session = Depends(get_db)):
    db_parcela = db.query(models.PagamentoParcela).filter(models.PagamentoParcela.id == parcela_id).first()
    if not db_parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    if db_parcela.status_pagamento == StatusPagamento.PAGO:
        raise HTTPException(status_code=400, detail="Esta parcela já consta como paga.")
    db_parcela.status_pagamento = StatusPagamento.PAGO
    db_parcela.data_pagamento_efetivo = baixa.data_pagamento_efetivo
    db.commit()
    db.refresh(db_parcela)
    return db_parcela

@router.delete("/{parcela_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_parcela(parcela_id: int, db: Session = Depends(get_db)):
    db_parcela = db.query(models.PagamentoParcela).filter(models.PagamentoParcela.id == parcela_id).first()
    if not db_parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    db.delete(db_parcela)
    db.commit()
