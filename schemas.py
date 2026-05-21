# schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from domain import TipoTransacao, TipoCliente, TipoParcela, StatusPagamento, StatusImovel

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