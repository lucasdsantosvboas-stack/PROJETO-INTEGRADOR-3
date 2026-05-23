from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from domain import TipoCliente
from utils.validacao import validar_cpf, normalizar_cpf
from utils.cep_api import buscar_endereco_por_cep
import asyncio

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])

@router.get("/", response_model=list[schemas.ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    """Lista todos os clientes cadastrados."""
    return db.query(models.Cliente).all()

@router.get("/{cliente_id}", response_model=schemas.ClienteResponse)
def buscar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Busca um cliente específico por ID."""
    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return db_cliente

@router.post("/", response_model=schemas.ClienteResponse, status_code=status.HTTP_201_CREATED)
async def criar_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    """
    Cria um novo cliente com validação de CPF e auto-preenchimento via CEP.
    
    - Se tipo = FISICA e CPF fornecido: valida CPF (será já validado por schema)
    - Se CEP fornecido: busca dados de endereço na BrasilAPI e auto-popula bairro, cidade, uf, logradouro
    """
    
    # Valida duplicação de CPF
    if cliente.cpf:
        cpf_existente = db.query(models.Cliente).filter(models.Cliente.cpf == cliente.cpf).first()
        if cpf_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado no sistema"
            )
    
    # Prepara dados para criar cliente
    dados_cliente = cliente.model_dump()
    
    # Define flag cpf_valido se CPF foi fornecido e é pessoa física
    if cliente.cpf and cliente.tipo == TipoCliente.FISICA:
        dados_cliente["cpf_valido"] = True
    else:
        dados_cliente["cpf_valido"] = False
    
    # Se CEP foi fornecido, busca dados de endereço na BrasilAPI
    if cliente.cep:
        try:
            endereco = await buscar_endereco_por_cep(cliente.cep)
            
            if endereco:
                # Auto-popula campos de endereço
                dados_cliente["logradouro"] = endereco.get("logradouro", dados_cliente.get("logradouro"))
                dados_cliente["bairro"] = endereco.get("bairro", dados_cliente.get("bairro"))
                dados_cliente["cidade"] = endereco.get("cidade", dados_cliente.get("cidade"))
                dados_cliente["uf"] = endereco.get("uf", dados_cliente.get("uf"))
            else:
                # CEP inválido, mas permite continuar com dados fornecidos manualmente
                pass
        except Exception as e:
            # Erro na busca de CEP, mas permite continuar com dados fornecidos
            print(f"Erro ao buscar CEP: {e}")
            pass
    
    # Remove campo 'cep' que não existe na tabela
    dados_cliente.pop("cep", None)
    
    # Cria cliente
    db_cliente = models.Cliente(**dados_cliente)
    db.add(db_cliente)
    
    try:
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar cliente: {str(e)}"
        )

@router.put("/{cliente_id}", response_model=schemas.ClienteResponse)
async def atualizar_cliente(cliente_id: int, cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    """
    Atualiza um cliente existente.
    
    Se CEP for fornecido, busca dados de endereço na BrasilAPI.
    """
    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Valida duplicação de CPF (se mudando)
    if cliente.cpf and cliente.cpf != db_cliente.cpf:
        cpf_existente = db.query(models.Cliente).filter(
            models.Cliente.cpf == cliente.cpf,
            models.Cliente.id != cliente_id
        ).first()
        if cpf_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado no sistema"
            )
    
    dados_cliente = cliente.model_dump()
    
    # Define flag cpf_valido
    if cliente.cpf and cliente.tipo == TipoCliente.FISICA:
        dados_cliente["cpf_valido"] = True
    
    # Se CEP foi fornecido, busca dados de endereço
    if cliente.cep:
        try:
            endereco = await buscar_endereco_por_cep(cliente.cep)
            
            if endereco:
                dados_cliente["logradouro"] = endereco.get("logradouro", dados_cliente.get("logradouro"))
                dados_cliente["bairro"] = endereco.get("bairro", dados_cliente.get("bairro"))
                dados_cliente["cidade"] = endereco.get("cidade", dados_cliente.get("cidade"))
                dados_cliente["uf"] = endereco.get("uf", dados_cliente.get("uf"))
        except Exception as e:
            print(f"Erro ao buscar CEP: {e}")
    
    dados_cliente.pop("cep", None)
    
    # Atualiza cliente
    for campo, valor in dados_cliente.items():
        setattr(db_cliente, campo, valor)
    
    try:
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar cliente: {str(e)}"
        )

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Deleta um cliente."""
    db_cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    db.delete(db_cliente)
    db.commit()
