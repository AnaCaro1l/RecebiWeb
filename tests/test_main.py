import pytest
from recebi import create_app
from recebi.ext.db import db
from recebi.models import Usuario

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

def test_carrinho_page(client):
    response = client.get('/carrinho.html')
    assert response.status_code == 200
    assert b"Carrinho" in response.data

def test_contato_page(client):
    response = client.get('/contato.html')
    assert response.status_code == 200
    assert b"Contato" in response.data

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
    assert "token" in data
    assert data["usuario"]["Nome"] == "Test User"
