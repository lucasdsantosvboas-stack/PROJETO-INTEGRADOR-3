# routers/imovel_router.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import models
import schemas
from database import get_db
from domain import StatusImovel, TipoTransacao, TipoImovel
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/api/v1/imoveis", tags=["Imóveis"])

# Configuração de upload
UPLOAD_DIR = Path("static/fotos_imoveis")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@router.get("/", response_model=list[schemas.ImovelResponse])
def listar_imoveis(db: Session = Depends(get_db)):
    """Lista todos os imóveis no painel administrativo."""
    return db.query(models.Imovel).order_by(models.Imovel.id.desc()).all()

@router.get("/filtrado", response_model=list[schemas.ImovelResponse])
def filtrar_imoveis(
    db: Session = Depends(get_db),
    bairro: str = Query(None, description="Filtrar por bairro"),
    tipo: TipoTransacao = Query(None, description="Filtrar por tipo de transação (VENDA/ALUGUEL)"),
    tipo_imovel: TipoImovel = Query(None, description="Filtrar por tipo de imóvel"),
    valor_min: float = Query(None, ge=0, description="Valor mínimo"),
    valor_max: float = Query(None, ge=0, description="Valor máximo")
):
    """
    Filtra imóveis disponíveis com múltiplos critérios.
    
    Query params:
    - bairro: string (opcional)
    - tipo: VENDA ou ALUGUEL (opcional)
    - tipo_imovel: tipo de imóvel (opcional)
    - valor_min: valor mínimo (opcional)
    - valor_max: valor máximo (opcional)
    """
    query = db.query(models.Imovel).filter(models.Imovel.status == StatusImovel.DISPONIVEL)
    
    # Aplica filtros
    if bairro:
        query = query.filter(models.Imovel.bairro.ilike(f"%{bairro}%"))
    
    if tipo:
        query = query.filter(models.Imovel.tipo_transacao == tipo)
    
    if tipo_imovel:
        query = query.filter(models.Imovel.tipo_imovel == tipo_imovel)
    
    if valor_min is not None:
        query = query.filter(models.Imovel.preco_atual >= valor_min)
    
    if valor_max is not None:
        query = query.filter(models.Imovel.preco_atual <= valor_max)
    
    # Ordena por data de criação (mais recentes primeiro)
    # Nota: Imovel não tem data_criacao. Se necessário, adicione campo de timestamp
    return query.order_by(models.Imovel.id.desc()).all()

@router.get("/bairros", response_model=list[str])
def listar_bairros(db: Session = Depends(get_db)):
    """Retorna lista de bairros únicos com imóveis disponíveis."""
    bairros = db.query(models.Imovel.bairro).filter(
        and_(
            models.Imovel.status == StatusImovel.DISPONIVEL,
            models.Imovel.bairro != None
        )
    ).distinct().order_by(models.Imovel.bairro).all()
    
    return [b[0] for b in bairros if b[0]]

@router.get("/tipos-imovel", response_model=list[str])
def listar_tipos_imovel():
    """Retorna lista de tipos de imóvel disponíveis."""
    return [tipo.value for tipo in TipoImovel]

@router.get("/tipos-transacao", response_model=list[str])
def listar_tipos_transacao():
    """Retorna lista de tipos de transação disponíveis."""
    return [tipo.value for tipo in TipoTransacao]

@router.post("/upload-foto", status_code=status.HTTP_200_OK)
async def fazer_upload_foto(file: UploadFile = File(...)):
    """
    Upload de foto de imóvel.
    
    Retorna:
    {
        "foto_url": "fotos_imoveis/abc123.png",
        "filename": "abc123.png"
    }
    """
    # Valida tipo de arquivo
    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Tipos aceitos: JPEG, PNG, GIF, WebP"
        )
    
    # Lê arquivo e valida tamanho
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Máximo: 5 MB"
        )
    
    # Gera nome único
    ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Salva arquivo
    try:
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Retorna caminho relativo
        relative_path = f"fotos_imoveis/{unique_filename}"
        return {
            "foto_url": relative_path,
            "filename": unique_filename
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )

@router.post("/{imovel_id}/fotos", response_model=schemas.FotoImovelResponse)
async def adicionar_foto_imovel(imovel_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Adiciona uma foto a um imóvel existente.
    """
    # Verifica se imóvel existe
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    # Valida tipo de arquivo
    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Tipos aceitos: JPEG, PNG, GIF, WebP"
        )
    
    # Lê arquivo e valida tamanho
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Arquivo muito grande. Máximo: 5 MB"
        )
    
    # Gera nome único
    ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Salva arquivo
    try:
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Calcula ordem (próximo número)
        max_ordem = db.query(models.FotoImovel).filter(
            models.FotoImovel.imovel_id == imovel_id
        ).count()
        
        # Cria registro de foto
        relative_path = f"fotos_imoveis/{unique_filename}"
        db_foto = models.FotoImovel(
            imovel_id=imovel_id,
            foto_url=relative_path,
            ordem=max_ordem
        )
        db.add(db_foto)
        db.commit()
        db.refresh(db_foto)
        
        return db_foto
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )

@router.post("/{imovel_id}/fotos/link", response_model=schemas.FotoImovelResponse)
def vincular_foto_imovel(imovel_id: int, foto: schemas.FotoImovelBase, db: Session = Depends(get_db)):
    """
    Associa uma foto que já foi salva no servidor à galeria de um imóvel existente.
    """
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    
    db_foto = models.FotoImovel(
        imovel_id=imovel_id,
        foto_url=foto.foto_url,
        ordem=foto.ordem
    )
    db.add(db_foto)
    db.commit()
    db.refresh(db_foto)
    return db_foto

@router.delete("/{imovel_id}/fotos/{foto_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_foto_imovel(imovel_id: int, foto_id: int, db: Session = Depends(get_db)):
    """
    Deleta uma foto de um imóvel.
    """
    db_foto = db.query(models.FotoImovel).filter(
        and_(
            models.FotoImovel.id == foto_id,
            models.FotoImovel.imovel_id == imovel_id
        )
    ).first()
    
    if not db_foto:
        raise HTTPException(status_code=404, detail="Foto não encontrada")
    
    # Remove arquivo físico
    try:
        file_path = UPLOAD_DIR / Path(db_foto.foto_url).name
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass  # Ignora erros ao deletar arquivo
    
    db.delete(db_foto)
    db.commit()

@router.post("/{imovel_id}/fotos/reordenar")
def reordenar_fotos(imovel_id: int, ordem_ids: list[int], db: Session = Depends(get_db)):
    """
    Reordena as fotos de um imóvel. Recebe lista de IDs na ordem desejada.
    """
    fotos = db.query(models.FotoImovel).filter(
        models.FotoImovel.imovel_id == imovel_id
    ).all()
    
    if len(fotos) != len(ordem_ids):
        raise HTTPException(status_code=400, detail="IDs de fotos inválidos")
    
    for nova_ordem, foto_id in enumerate(ordem_ids):
        foto = next((f for f in fotos if f.id == foto_id), None)
        if not foto:
            raise HTTPException(status_code=404, detail=f"Foto {foto_id} não encontrada")
        foto.ordem = nova_ordem
    
    db.commit()
    return {"message": "Fotos reordenadas com sucesso"}

@router.get("/{imovel_id}", response_model=schemas.ImovelResponse)
def buscar_imovel(imovel_id: int, db: Session = Depends(get_db)):
    """Busca um imóvel específico por ID."""
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    return db_imovel

@router.post("/", response_model=schemas.ImovelResponse, status_code=status.HTTP_201_CREATED)
def criar_imovel(imovel: schemas.ImovelCreate, db: Session = Depends(get_db)):
    """Cria um novo imóvel com foto opcional."""
    db_imovel = models.Imovel(**imovel.model_dump())
    db.add(db_imovel)
    db.commit()
    db.refresh(db_imovel)
    return db_imovel

@router.put("/{imovel_id}", response_model=schemas.ImovelResponse)
def atualizar_imovel(imovel_id: int, imovel: schemas.ImovelCreate, db: Session = Depends(get_db)):
    """Atualiza um imóvel existente."""
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    for campo, valor in imovel.model_dump(exclude_unset=True).items():
        setattr(db_imovel, campo, valor)
    db.commit()
    db.refresh(db_imovel)
    return db_imovel

@router.patch("/{imovel_id}/status", response_model=schemas.ImovelResponse)
def atualizar_status(imovel_id: int, status_update: schemas.ImovelUpdateStatus, db: Session = Depends(get_db)):
    """Atualiza status de um imóvel e registra no histórico."""
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    if db_imovel.status != status_update.status:
        db.add(models.HistoricoStatus(
            imovel_id=db_imovel.id,
            status_anterior=db_imovel.status,
            status_novo=status_update.status
        ))
        db_imovel.status = status_update.status
        db.commit()
        db.refresh(db_imovel)
    return db_imovel

@router.delete("/{imovel_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_imovel(imovel_id: int, db: Session = Depends(get_db)):
    """Deleta um imóvel."""
    db_imovel = db.query(models.Imovel).filter(models.Imovel.id == imovel_id).first()
    if not db_imovel:
        raise HTTPException(status_code=404, detail="Imóvel não encontrado")
    db.delete(db_imovel)
    db.commit()
