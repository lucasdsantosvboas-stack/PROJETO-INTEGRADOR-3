from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/v1/visitas", tags=["Visitas"])

@router.get("/", response_model=list[schemas.VisitaResponse])
def listar_visitas(db: Session = Depends(get_db)):
    return db.query(models.Visita).order_by(models.Visita.data_visita.desc()).all()

@router.post("/", response_model=schemas.VisitaResponse, status_code=status.HTTP_201_CREATED)
def agendar_visita(visita: schemas.VisitaCreate, db: Session = Depends(get_db)):
    db_visita = models.Visita(**visita.model_dump())
    db.add(db_visita)
    db.commit()
    db.refresh(db_visita)
    return db_visita