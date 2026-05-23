# Integração com BrasilAPI para validação de CEP
import httpx
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Cache em memória para reduzir chamadas à API
_cache_cep: Dict[str, tuple[dict, datetime]] = {}
CACHE_DURATION_MINUTES = 60


async def buscar_endereco_por_cep(cep: str) -> Optional[Dict[str, Any]]:
    """
    Busca dados de endereço via BrasilAPI usando um CEP.
    
    A função valida o CEP, verifica cache e faz requisição à BrasilAPI.
    
    Args:
        cep: String com CEP (pode ter máscara ou não)
        
    Returns:
        Dict com chaves: logradouro, bairro, cidade, uf
        None se CEP for inválido ou API falhar
        
    Exemplo:
        >>> resultado = await buscar_endereco_por_cep("01310100")
        >>> resultado
        {'logradouro': 'Avenida Paulista', 'bairro': 'Bela Vista', 
         'cidade': 'São Paulo', 'uf': 'SP'}
    """
    
    if not cep:
        return None
    
    # Normaliza CEP: remove caracteres especiais
    cep_limpo = ''.join(filter(str.isdigit, cep))
    
    # Valida formato: deve ter 8 dígitos
    if len(cep_limpo) != 8:
        return None
    
    # Verifica cache
    if cep_limpo in _cache_cep:
        dados_cache, timestamp_cache = _cache_cep[cep_limpo]
        if datetime.now() - timestamp_cache < timedelta(minutes=CACHE_DURATION_MINUTES):
            return dados_cache
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"https://brasilapi.com.br/api/cep/v1/{cep_limpo}"
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrai informações relevantes (mapeando campos da API)
                resultado = {
                    "logradouro": data.get("street", ""),
                    "bairro": data.get("neighborhood", ""),
                    "cidade": data.get("city", ""),
                    "uf": data.get("state", "")
                }
                
                # Cacheia resultado
                _cache_cep[cep_limpo] = (resultado, datetime.now())
                
                return resultado
            else:
                # CEP não encontrado ou erro da API
                return None
                
    except httpx.RequestError as e:
        # Erro de conexão
        print(f"Erro ao conectar com BrasilAPI: {e}")
        return None
    except Exception as e:
        # Outro erro
        print(f"Erro ao buscar CEP: {e}")
        return None


def limpar_cache_cep():
    """
    Limpa o cache de CEPs em memória.
    """
    global _cache_cep
    _cache_cep.clear()
