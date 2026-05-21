# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import models
from database import engine
from routers import imovel_router, cliente_router, transacao_router, pagamento_router, corretor_router

# Cria as tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Imobiliária - ERP", 
    description="Sistema de gestão imobiliária com tratamento de erros globais.",
    version="1.0.0"
)

# Toda vez que qualquer rota disparar um IntegrityError, o FastAPI joga o erro para cá.
@app.exception_handler(IntegrityError)
async def integridade_referencial_handler(request: Request, exc: IntegrityError):
    # Ao invés de um erro 500 caótico, devolvemos um erro 400 (Bad Request) limpo.
    return JSONResponse(
        status_code=400,
        content={"detail": "Operação bloqueada: Este registro está vinculado a outros dados essenciais do sistema (ex: contratos ou históricos)."},
    )


from routers import imovel_router, cliente_router, transacao_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Imobiliária - ERP", 
    version="1.0.0"
)

@app.exception_handler(IntegrityError)
async def integridade_referencial_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Operação bloqueada: Este registro está vinculado a outros dados essenciais do sistema."},
    )

# Acoplamento dos roteadores
app.include_router(imovel_router.router)
app.include_router(cliente_router.router)
app.include_router(transacao_router.router)
app.include_router(pagamento_router.router)
app.include_router(corretor_router.router)