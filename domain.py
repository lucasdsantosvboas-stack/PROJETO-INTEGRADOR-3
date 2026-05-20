# domain.py
import enum

class StatusImovel(str, enum.Enum):
    DISPONIVEL = "DISPONIVEL"
    ALUGADO = "ALUGADO"
    VENDIDO = "VENDIDO"
    INATIVO = "INATIVO"