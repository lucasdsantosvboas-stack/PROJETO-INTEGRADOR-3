from database import SessionLocal
from models import Usuario
import hashlib

db = SessionLocal()

# Verifica se usuário já existe
user = db.query(Usuario).filter(Usuario.username == "admin").first()
if user:
    print("Usuario 'admin' ja existe")
else:
    # Cria novo usuario com hash simples
    senha = "123456"
    hash_senha = hashlib.sha256(senha.encode()).hexdigest()
    novo_usuario = Usuario(
        username="admin",
        senha_hash=hash_senha,
        ativo=True
    )
    db.add(novo_usuario)
    db.commit()
    print("Usuario criado: admin / 123456")

db.close()

