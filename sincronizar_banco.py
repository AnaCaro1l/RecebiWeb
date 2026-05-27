from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("🧹 Apagando as tabelas antigas (se existirem)...")
    db.drop_all()
    
    print("🏗️ Criando as novas tabelas com a estrutura atualizada...")
    db.create_all()
    
    print("👤 Recriando o usuário Síndico padrão...")
    # Atenção: O Enum do banco agora exige a primeira letra maiúscula ('Sindico', 'Porteiro', 'Morador')
    sindico = Usuario(
        nome='Administrador Principal', 
        email='sindico@recebi.com', 
        senha=generate_password_hash('senha123'), 
        perfil='Sindico', 
        is_active=True
    )
    
    db.session.add(sindico)
    db.session.commit()
    
    print("✅ Sincronização concluída com sucesso! Banco pronto para uso.")