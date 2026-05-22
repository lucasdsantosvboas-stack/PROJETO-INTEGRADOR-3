from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/v1/leads", tags=["Leads"])

@router.get("/", response_model=list[schemas.LeadResponse])
def listar_leads(db: Session = Depends(get_db)):
    return db.query(models.Lead).all()

@router.get("/{lead_id}", response_model=schemas.LeadResponse)
def buscar_lead(lead_id: int, db: Session = Depends(get_db)):
    db_lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return db_lead

@router.post("/", response_model=schemas.LeadResponse, status_code=status.HTTP_201_CREATED)
def criar_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    db_lead = models.Lead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead