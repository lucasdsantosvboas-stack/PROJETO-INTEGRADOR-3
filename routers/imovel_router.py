# routers/imovel_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/v1/imoveis", tags=["Imóveis"])

@router.get("/", response_model=list[schemas.ImovelResponse])
def listar_imoveis(db: Session = Depends(get_db)):
    return db.query(models.Imovel).all()

@router.get("/{imovel_id}", response_model=schemas.ImovelResponse)
def buscar_imovel(imovel_id: int, db: Session = Depends(get_db)):
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return db_imovel

@router.post("/", response_model=schemas.ImovelResponse, status_code=status.HTTP_201_CREATED)
def criar_imovel(imovel: schemas.ImovelCreate, db: Session = Depends(get_db)):
    db_imovel = models.Imovel(**imovel.model_dump())
    db.add(db_imovel)
    db.commit()
    db.refresh(db_imovel)
    return db_imovel

@router.put("/{imovel_id}", response_model=schemas.ImovelResponse)
def atualizar_imovel(imovel_id: int, imovel: schemas.ImovelCreate, db: Session = Depends(get_db)):
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    for campo, valor in imovel.model_dump().items():
        setattr(db_imovel, campo, valor)
    db.commit()
    db.refresh(db_imovel)
    return db_imovel

@router.patch("/{imovel_id}/status", response_model=schemas.ImovelResponse)
def atualizar_status(imovel_id: int, status_update: schemas.ImovelUpdateStatus, db: Session = Depends(get_db)):
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    if db_imovel.status != status_update.status:
        db.add(models.HistoricoStatus(
            imovel_id=db_imovel.id,
            status_anterior=db_imovel.status,
            status_novo=status_update.status
        ))
        db_imovel.status = status_update.status
        db.commit()
        db.refresh(db_imovel)
    return db_imovel

@router.delete("/{imovel_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_imovel(imovel_id: int, db: Session = Depends(get_db)):
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    db.delete(db_imovel)
    db.commit()
