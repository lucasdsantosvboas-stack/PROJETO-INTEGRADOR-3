# domain.py
import enum

class StatusImovel(str, enum.Enum):
    DISPONIVEL = "DISPONIVEL"
    ALUGADO = "ALUGADO"
    VENDIDO = "VENDIDO"
    INATIVO = "INATIVO"

class TipoCliente(str, enum.Enum):
    FISICA = "FISICA"
    JURIDICA = "JURIDICA"

class TipoTransacao(str, enum.Enum):
    VENDA = "VENDA"
    ALUGUEL = "ALUGUEL"

class TipoParcela(str, enum.Enum):
    SINAL = "SINAL"
    COMISSAO = "COMISSAO"
    ALUGUEL = "ALUGUEL"
    REAJUSTE = "REAJUSTE"
    OUTRO = "OUTRO"

class StatusPagamento(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    ATRASADO = "ATRASADO"
    CANCELADO = "CANCELADO"
