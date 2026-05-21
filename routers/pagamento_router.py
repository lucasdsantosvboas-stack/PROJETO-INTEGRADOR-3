from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/v1/parcelas", tags=["Financeiro"])

@router.post("/", response_model=schemas.PagamentoParcelaResponse, status_code=status.HTTP_201_CREATED)
def criar_parcela(parcela: schemas.PagamentoParcelaCreate, db: Session = Depends(get_db)):
    db_parcela = models.PagamentoParcela(**parcela.model_dump())
    db.add(db_parcela)
    db.commit()
    db.refresh(db_parcela)
    return db_parcela

@router.patch("/{parcela_id}/pagar", response_model=schemas.PagamentoParcelaResponse)
def dar_baixa_parcela(parcela_id: int, baixa: schemas.PagamentoBaixa, db: Session = Depends(get_db)):
    db_parcela = db.query(models.PagamentoParcela).filter(models.PagamentoParcela.id == parcela_id).first()
    
    if not db_parcela:
        raise HTTPException(status_code=404, detail="Parcela não encontrada")
    
    if db_parcela.status_pagamento == models.StatusPagamento.PAGO:
        raise HTTPException(status_code=400, detail="Esta parcela já consta como paga.")
        
    db_parcela.status_pagamento = models.StatusPagamento.PAGO
    db_parcela.data_pagamento_efetivo = baixa.data_pagamento_efetivo
    
    db.commit()
    db.refresh(db_parcela)
    return db_parcela