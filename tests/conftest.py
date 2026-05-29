import os
import sys
import pytest
from flask_jwt_extended import create_access_token

# Força o Python e o Pytest a enxergarem a pasta raiz do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from recebi import create_app  
from recebi.ext.db import db
from recebi.models.usuario import Usuario
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # Banco isolado em memória
        "JWT_SECRET_KEY": "test_jwt_key_99999_super_long_and_secure_secret_key_for_testing"
    })

    with app.app_context():
        db.create_all()
        
        # Cria um usuário Síndico administrativo real para o ambiente de testes
        sindico = Usuario(
            nome="Síndico de Teste",
            email="sindico@teste.com",
            senha=generate_password_hash("123456"),
            perfil="Sindico",
            is_active=True
        )
        db.session.add(sindico)
        db.session.commit()
        
        # Guarda o ID gerado para usar na criação do Token legítimo
        pytest.sindico_id = str(sindico.id)
        
    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    """Gera um cabeçalho de autenticação JWT legítimo contendo a claim 'perfil' exigida pelo back-end"""
    with app.app_context():
        token = create_access_token(
            identity=pytest.sindico_id,
            additional_claims={"perfil": "Sindico"}
        )
        return {"Authorization": f"Bearer {token}"}