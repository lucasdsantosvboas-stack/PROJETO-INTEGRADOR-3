# schemas.py
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime, date
from domain import TipoTransacao, TipoCliente, TipoParcela, StatusPagamento, StatusImovel, StatusLead, StatusVisita

# Base com regras estritas de validação
class ImovelBase(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=100, description="Título do anúncio")
    descricao: Optional[str] = Field(None, max_length=500)
    preco_atual: float = Field(..., gt=0, description="O preço deve ser maior que zero")
    status: StatusImovel = StatusImovel.DISPONIVEL
    endereco: str = Field(..., min_length=10, max_length=255)

# Schema usado no POST (quando o usuário envia os dados via NiceGUI)
# Não tem ID, porque o banco quem gera.
class ImovelCreate(ImovelBase):
    pass 

# Schema usado no GET e no retorno do POST (quando o FastAPI devolve pro NiceGUI)
class ImovelResponse(ImovelBase):
    id: int

    # Essa configuração permite que o Pydantic leia diretamente o objeto do SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

class ImovelUpdateStatus(BaseModel):
    status: StatusImovel

from domain import TipoCliente

class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100, description="Nome completo ou Razão Social")
    contato: str = Field(..., min_length=8, max_length=50, description="Telefone ou Email de contacto")
    tipo: TipoCliente

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class TransacaoBase(BaseModel):
    imovel_id: int
    proprietario_id: int
    cliente_id: int
    tipo_contrato: TipoTransacao
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    valor_total_contrato: float = Field(..., gt=0)
    
    comissao_percentual: Optional[float] = None
    sinal_negocio: Optional[float] = None
    reajuste_anual_percentual: Optional[float] = None

class TransacaoCreate(TransacaoBase):
    pass

class TransacaoResponse(TransacaoBase):
    id: int
    data_inicio: datetime

    model_config = ConfigDict(from_attributes=True)

class PagamentoParcelaBase(BaseModel):
    transacao_id: int
    valor_parcela: float = Field(..., gt=0)
    data_vencimento: date
    tipo_parcela: TipoParcela

class PagamentoParcelaCreate(PagamentoParcelaBase):
    pass

# Schema para quando o cliente paga a fatura
class PagamentoBaixa(BaseModel):
    data_pagamento_efetivo: date

class PagamentoParcelaResponse(PagamentoParcelaBase):
    id: int
    status_pagamento: StatusPagamento
    data_pagamento_efetivo: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

class CorretorBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    registro_profissional: str = Field(..., description="CRECI ou similar")

class CorretorCreate(CorretorBase):
    senha: str = Field(..., min_length=8, description="Senha forte para acesso")

class CorretorResponse(CorretorBase):
    id: int
    ativo: bool
    # Repare: não há campo de senha aqui. O frontend nunca recebe a senha de volta.

    model_config = ConfigDict(from_attributes=True)

class LeadBase(BaseModel):
    nome: str = Field(..., min_length=3)
    telefone: str = Field(..., min_length=8)
    interesse: Optional[str] = None
    corretor_id: int

class LeadCreate(LeadBase):
    pass

class LeadResponse(LeadBase):
    id: int
    status: StatusLead
    model_config = ConfigDict(from_attributes=True)

class VisitaBase(BaseModel):
    data_visita: datetime
    imovel_id: int
    corretor_id: int
    lead_id: int

class VisitaCreate(VisitaBase):
    pass

class VisitaResponse(VisitaBase):
    id: int
    status: StatusVisita
    feedback_comentario: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)