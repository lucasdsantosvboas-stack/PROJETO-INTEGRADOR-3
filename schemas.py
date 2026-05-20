# schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from domain import StatusImovel

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