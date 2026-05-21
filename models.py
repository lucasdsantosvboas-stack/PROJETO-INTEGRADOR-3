# models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Date, ForeignKey, String, Numeric, Enum as SQLEnum
from typing import Optional
from datetime import datetime
from domain import TipoTransacao, StatusPagamento, StatusImovel, TipoCliente, TipoParcela
from sqlalchemy import Date

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


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    contato: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo: Mapped[TipoCliente] = mapped_column(SQLEnum(TipoCliente), nullable=False)

class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Chaves Estrangeiras
    imovel_id: Mapped[int] = mapped_column(ForeignKey("imoveis.id"), nullable=False)
    proprietario_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), nullable=False) # Comprador ou Locatário
    
    # Dados Base do Contrato
    tipo_contrato: Mapped[TipoTransacao] = mapped_column(SQLEnum(TipoTransacao), nullable=False)
    data_inicio: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    data_fim: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    valor_total_contrato: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    
    # Campos Polimórficos (Opcionais dependendo se é Venda ou Aluguel)
    comissao_percentual: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True) # Para Venda
    sinal_negocio: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True) # Para Venda
    reajuste_anual_percentual: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True) # Para Aluguel

class PagamentoParcela(Base):
    __tablename__ = "pagamento_parcelas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transacao_id: Mapped[int] = mapped_column(ForeignKey("transacoes.id"), nullable=False)
    
    valor_parcela: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    data_vencimento: Mapped[datetime] = mapped_column(Date, nullable=False)
    data_pagamento_efetivo: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    
    status_pagamento: Mapped[StatusPagamento] = mapped_column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE)
    tipo_parcela: Mapped[TipoParcela] = mapped_column(SQLEnum(TipoParcela), nullable=False)

class Corretor(Base):
    __tablename__ = "corretores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    registro_profissional: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # Ex: CRECI
    
    # NUNCA salve a senha pura. 
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True)

class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    interesse: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[StatusLead] = mapped_column(SQLEnum(StatusLead), default=StatusLead.NOVO)
    
    # Qual corretor está cuidando desse lead?
    corretor_id: Mapped[int] = mapped_column(ForeignKey("corretores.id"), nullable=False)

class Visita(Base):
    __tablename__ = "visitas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    data_visita: Mapped[datetime] = mapped_column(nullable=False)
    feedback_comentario: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[StatusVisita] = mapped_column(SQLEnum(StatusVisita), default=StatusVisita.AGENDADA)
    
    # Amarrações do evento
    imovel_id: Mapped[int] = mapped_column(ForeignKey("imoveis.id"), nullable=False)
    corretor_id: Mapped[int] = mapped_column(ForeignKey("corretores.id"), nullable=False)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)