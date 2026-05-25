import models
from database import SessionLocal
from domain import StatusImovel, TipoTransacao, TipoImovel
import hashlib

def popular_banco():
    db = SessionLocal()
    
    print("🔄 Inserindo dados fictícios...")
    
    # Criar Imóveis
    imoveis = [
        models.Imovel(
            titulo="Apartamento de Luxo",
            descricao="Lindo apartamento com 3 quartos, varanda gourmet e 2 vagas.",
            preco_atual=850000.00,
            status=StatusImovel.DISPONIVEL,
            endereco="Av. Principal, 1000, Centro, São Paulo - SP",
            bairro="Centro",
            tipo_imovel=TipoImovel.APARTAMENTO,
            tipo_transacao=TipoTransacao.VENDA
        ),
        models.Imovel(
            titulo="Casa Térrea com Piscina",
            descricao="Casa espaçosa com 4 quartos, área de lazer com churrasqueira e piscina.",
            preco_atual=1200000.00,
            status=StatusImovel.DISPONIVEL,
            endereco="Rua das Flores, 500, Jardim Primavera, São Paulo - SP",
            bairro="Jardim Primavera",
            tipo_imovel=TipoImovel.CASA,
            tipo_transacao=TipoTransacao.VENDA
        ),
        models.Imovel(
            titulo="Sala Comercial",
            descricao="Sala com 40m², banheiro privativo, portaria 24h.",
            preco_atual=2500.00,
            status=StatusImovel.DISPONIVEL,
            endereco="Av. Comercial, 300, Redentora, São Paulo - SP",
            bairro="Redentora",
            tipo_imovel=TipoImovel.COMERCIAL,
            tipo_transacao=TipoTransacao.ALUGUEL
        )
    ]
    
    db.add_all(imoveis)
    db.commit()
    print("✅ 3 Imóveis fictícios criados e já listados no Catálogo!")
    db.close()

if __name__ == "__main__":
    popular_banco()