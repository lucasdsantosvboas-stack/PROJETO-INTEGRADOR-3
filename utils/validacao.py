# Utilitários de Validação
from brutils.cpf import is_valid as is_valid_cpf, format_cpf
from typing import Optional


def validar_cpf(cpf: str) -> bool:
    """
    Valida um CPF usando brutils (verifica formato e dígitos verificadores).
    
    Args:
        cpf: String com CPF (pode ter pontuação ou não)
        
    Returns:
        True se CPF é válido, False caso contrário
    """
    if not cpf:
        return False
    
    try:
        return is_valid_cpf(cpf)
    except Exception:
        return False


def normalizar_cpf(cpf: str) -> Optional[str]:
    """
    Remove caracteres especiais do CPF, deixando apenas dígitos.
    
    Args:
        cpf: String com CPF (pode ter pontuação)
        
    Returns:
        String com 11 dígitos ou None se inválida
    """
    if not cpf:
        return None
    
    # Remove caracteres não numéricos
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf_limpo) == 11:
        return cpf_limpo
    
    return None


def formatar_cpf(cpf: str) -> str:
    """
    Formata CPF para padrão brasileiro (XXX.XXX.XXX-XX).
    
    Args:
        cpf: String com 11 dígitos
        
    Returns:
        CPF formatado
    """
    if len(cpf) != 11:
        return cpf
    
    try:
        return format_cpf(cpf)
    except Exception:
        return cpf
