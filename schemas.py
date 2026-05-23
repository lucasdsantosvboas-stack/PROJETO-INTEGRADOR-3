# Modelos de validação de dados da API (Esquemas do Pydantic)
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import Optional
from datetime import datetime, date
from domain import TipoTransacao, TipoCliente, TipoParcela, StatusPagamento, StatusImovel, StatusLead, StatusVisita, TipoImovel
from utils.validacao import validar_cpf, normalizar_cpf

# Base com regras estritas de validação
class ImovelBase(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=100, description="Título do anúncio")
    descricao: Optional[str] = Field(None, max_length=500)
    preco_atual: float = Field(..., gt=0, description="O preço deve ser maior que zero")
    status: StatusImovel = StatusImovel.DISPONIVEL
    endereco: str = Field(..., min_length=10, max_length=255)
    foto_url: Optional[str] = Field(None, description="Caminho relativo da foto no servidor")
    bairro: Optional[str] = Field(None, max_length=100, description="Bairro do imóvel")
    tipo_imovel: Optional[TipoImovel] = Field(None, description="Tipo: Apartamento, Casa, Comercial, etc")
    tipo_transacao: Optional[TipoTransacao] = Field(None, description="Tipo de transação: VENDA ou ALUGUEL")

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


class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100, description="Nome completo ou Razão Social")
    contato: str = Field(..., min_length=8, max_length=50, description="Telefone ou Email de contacto")
    tipo: TipoCliente

class ClienteCreate(ClienteBase):
    cpf: Optional[str] = Field(None, description="CPF (apenas para Pessoa Física, será validado)")
    cep: Optional[str] = Field(None, description="CEP para auto-preenchimento de endereço via BrasilAPI")
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    uf: Optional[str] = Field(None, max_length=2)
    logradouro: Optional[str] = Field(None, max_length=255)
    
    @field_validator('cpf')
    @classmethod
    def validar_cpf_campo(cls, v: Optional[str], info) -> Optional[str]:
        """Valida CPF se fornecido e tipo for PESSOA_FISICA."""
        if v is None:
            return v
        
        # Normaliza CPF (remove caracteres especiais)
        cpf_limpo = normalizar_cpf(v)
        if cpf_limpo is None:
            raise ValueError("CPF deve conter 11 dígitos numéricos")
        
        # Valida dígitos verificadores se tipo for PESSOA_FISICA
        if info.data.get('tipo') == TipoCliente.FISICA:
            if not validar_cpf(cpf_limpo):
                raise ValueError("CPF inválido (dígitos verificadores não conferem)")
        
        return cpf_limpo

class ClienteResponse(ClienteBase):
    id: int
    cpf: Optional[str] = None
    cpf_valido: bool = False
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    logradouro: Optional[str] = None

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

class UsuarioCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str