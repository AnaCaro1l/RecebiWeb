from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Verifica se o email já existe para não duplicar se você rodar o script duas vezes
    if not Usuario.query.filter_by(email='sindico@recebi.com').first():
        senha_criptografada = generate_password_hash('senha123')
        
        sindico = Usuario(
            nome='Administrador Principal', 
            email='sindico@recebi.com', 
            senha=senha_criptografada, 
            perfil='sindico'
        )
        
        db.session.add(sindico)
        db.session.commit()
        print("Síndico criado com sucesso! Email: sindico@recebi.com | Senha: senha123")
    else:
        print("O síndico já existe no banco de dados.")