# Regras de domínio (Enums e constantes)
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

class StatusLead(str, enum.Enum):
    NOVO = "NOVO"
    EM_ATENDIMENTO = "EM_ATENDIMENTO"
    CONVERTIDO = "CONVERTIDO"
    PERDIDO = "PERDIDO"

class StatusVisita(str, enum.Enum):
    AGENDADA = "AGENDADA"
    REALIZADA = "REALIZADA"
    CANCELADA = "CANCELADA"