import models
from database import engine

print("🔄 Conectando ao banco de dados...")

print("🗑️  Apagando tabelas antigas...")
models.Base.metadata.drop_all(bind=engine)

print("✨ Recriando tabelas com as novas colunas (bairro, foto_url, cpf)...")
models.Base.metadata.create_all(bind=engine)

print("✅ Banco de dados atualizado com sucesso!")