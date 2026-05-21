# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, ForeignKey, Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# String de conexão. O SQLite criará um arquivo local chamado 'imobiliaria.db'
SQLALCHEMY_DATABASE_URL = "sqlite:///./imobiliaria.db"

# connect_args={"check_same_thread": False} é uma exigência específica do SQLite com FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# A 'fábrica' de sessões. Cada requisição na API abrirá uma sessão e a fechará no final.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency injection para o FastAPI: abre uma sessão por requisição e garante o fechamento.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()