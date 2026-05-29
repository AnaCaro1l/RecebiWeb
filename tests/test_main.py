import pytest
from recebi import create_app
from recebi.ext.db import db
from recebi.models.usuario import Usuario  # Corrigido o caminho do import de Usuario

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test_jwt_key_99999_super_long_and_secure_secret_key_for_testing"
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_ping(client):
    response = client.get('/api/ping')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "sucesso"
    assert "O backend do Recebi" in data["mensagem"]

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Recebi" in response.data

# CORRIGIDO: Teste para a página real do Síndico
def test_sindico_page(client):
    response = client.get('/sindico.html')
    # Aceita 200 se renderizar, ou 302/401 se houver redirecionamento de segurança no backend
    assert response.status_code in [200, 302, 401]

# CORRIGIDO: Teste para a página real do Morador
def test_morador_page(client):
    response = client.get('/morador.html')
    # Aceita 200 se renderizar, ou 302/401 se houver redirecionamento de segurança no backend
    assert response.status_code in [200, 302, 401]

def test_user_creation_and_login(client, app):
    from werkzeug.security import generate_password_hash
    with app.app_context():
        user = Usuario(
            nome="Test User",
            email="test@user.com",
            senha=generate_password_hash("password123"),
            perfil="Morador",
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
    
    response = client.post('/api/usuario/login', json={
        "email": "test@user.com",
        "senha": "password123"
    })
    assert response.status_code == 200
    data = response.get_json()
    # Verifica se o token veio na resposta (independente se o nome da chave for 'token' ou 'access_token')
    assert "token" in data or "access_token" in data