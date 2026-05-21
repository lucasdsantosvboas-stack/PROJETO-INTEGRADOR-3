# routers/imovel_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

# O APIRouter agrupa nossas rotas. Tudo aqui já começa com /api/v1/imoveis
router = APIRouter(prefix="/api/v1/imoveis", tags=["Imóveis"])

@router.post("/", response_model=schemas.ImovelResponse, status_code=status.HTTP_201_CREATED)
def criar_imovel(imovel: schemas.ImovelCreate, db: Session = Depends(get_db)):
    db_imovel = models.Imovel(**imovel.model_dump())
    db.add(db_imovel)
    db.commit()
    db.refresh(db_imovel)
    return db_imovel

# Rota cirúrgica: Apenas o status é alterado.
@router.patch("/{imovel_id}/status", response_model=schemas.ImovelResponse)
def atualizar_status(imovel_id: int, status_update: schemas.ImovelUpdateStatus, db: Session = Depends(get_db)):
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Só fazemos algo se o status realmente estiver mudando
    if db_imovel.status != status_update.status:
        # 1. Instancia o histórico com o status velho e o novo
        novo_historico = models.HistoricoStatus(
            imovel_id=db_imovel.id,
            status_anterior=db_imovel.status,
            status_novo=status_update.status
        )
        # 2. Adiciona o histórico na sessão
        db.add(novo_historico)
        
        # 3. Atualiza o status do imóvel
        db_imovel.status = status_update.status
        
        # 4. Salva TUDO junto. Se o banco cair aqui, nem o imóvel atualiza, nem o histórico é gerado pela metade.
        db.commit()
        db.refresh(db_imovel)
    
    return db_imovel