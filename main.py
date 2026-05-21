# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import models
from database import engine
from routers import auth_router, imovel_router, cliente_router, transacao_router, pagamento_router, corretor_router

# Cria as tabelas no banco
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Imobiliária - ERP",
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