# Configuração principal da API
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
import models
from database import engine
from routers import auth_router, imovel_router, cliente_router, transacao_router, pagamento_router, corretor_router, lead_router, visita_router
from pathlib import Path

# Cria as tabelas no banco
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API IMOBFACIL",
    description="Sistema de gestão imobiliária.",
    version="1.0.0"
)

@app.exception_handler(IntegrityError)
async def integridade_referencial_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Operação bloqueada: Este registro está vinculado a outros dados essenciais do sistema."},
    )

# Roteadores
app.include_router(auth_router.router)
app.include_router(imovel_router.router)
app.include_router(cliente_router.router)
app.include_router(transacao_router.router)
app.include_router(pagamento_router.router)
app.include_router(corretor_router.router)
app.include_router(lead_router.router)
app.include_router(visita_router.router)

# Servir arquivos estáticos (fotos de imóveis)
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Endpoint raiz
@app.get("/")
async def root():
    """Redireciona para o catálogo de imóveis."""
    return {
        "message": "Bem-vindo à API IMOBFACIL",
        "endpoints": {
            "api_docs": "/docs",
            "imoveis": "/api/v1/imoveis",
            "imoveis_filtrados": "/api/v1/imoveis/filtrado/",
            "clientes": "/api/v1/clientes",
            "catalogo_frontend": "http://localhost:8000 (ao executar frontend.py)"
        }
    }