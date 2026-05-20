# models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, String, Numeric, Enum as SQLEnum
from typing import Optional
from domain import StatusImovel
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Imovel(Base):
    __tablename__ = "imoveis"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(String(500))
    # Usamos Numeric para lidar com dinheiro com precisão no banco
    preco_atual: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False) 
    status: Mapped[StatusImovel] = mapped_column(SQLEnum(StatusImovel), default=StatusImovel.DISPONIVEL)
    endereco: Mapped[str] = mapped_column(String(255), nullable=False)

class HistoricoStatus(Base):
    __tablename__ = "historico_status"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    imovel_id: Mapped[int] = mapped_column(ForeignKey("imoveis.id"), nullable=False)
    status_anterior: Mapped[StatusImovel] = mapped_column(SQLEnum(StatusImovel), nullable=False)
    status_novo: Mapped[StatusImovel] = mapped_column(SQLEnum(StatusImovel), nullable=False)
    data_mudanca: Mapped[datetime] = mapped_column(default=datetime.utcnow)