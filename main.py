# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, SessionLocal

# Isso cria as tabelas no banco de dados automaticamente (útil para o MVP)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Imobiliária - ERP", version="1.0.0")

# Dependência do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rota POST: O Pydantic valida a entrada (ImovelCreate) e a saída (ImovelResponse)
@app.post("/api/v1/imoveis", response_model=schemas.ImovelResponse)
def criar_imovel(imovel: schemas.ImovelCreate, db: Session = Depends(get_db)):
    
    # 1. Neste ponto da execução, o Pydantic já garantiu que os dados estão corretos.
    # 2. Desempacotamos o dicionário do Pydantic direto no modelo SQLAlchemy
    db_imovel = models.Imovel(**imovel.model_dump())
    
    # 3. Adicionamos e 'comitamos' no banco
    db.add(db_imovel)
    db.commit()
    db.refresh(db_imovel)
    
    # 4. Retornamos o objeto. O FastAPI, usando o response_model, converte de volta para JSON.
    return db_imovel