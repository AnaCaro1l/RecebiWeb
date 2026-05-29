import pytest
from flask_jwt_extended import create_access_token
from recebi.ext.db import db
from recebi.models.usuario import Usuario
from recebi.models.encomenda import Encomenda

def test_listar_encomendas_porteiro_sem_autenticacao(client):
    """Garante que a rota de encomendas do porteiro bloqueia acessos sem Token JWT"""
    response = client.get("/api/porteiro/encomendas")
    assert response.status_code == 401

def test_registrar_encomenda_sucesso(client, app):
    """Testa o registro de uma nova encomenda feita pelo porteiro de forma legítima"""
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    with app.app_context():
        db.session.remove()
        
        # Cria as entidades de teste necessárias
        porteiro = Usuario(nome="Porteiro Teste", email="porteiro@teste.com", senha="123", perfil="Porteiro", is_active=True)
        morador = Usuario(nome="Morador Teste", email="morador@teste.com", senha="123", perfil="Morador", apartamento="101", is_active=True)
        db.session.add_all([porteiro, morador])
        db.session.commit()
        
        id_porteiro = str(porteiro.id)
        id_morador = morador.id

        token_porteiro = create_access_token(identity=id_porteiro, additional_claims={"perfil": "Porteiro"})
        headers = {"Authorization": f"Bearer {token_porteiro}"}
        
        payload = {
            "morador_id": id_morador,
            "descricao": "Pacote Amazon Teste",
            "codigo_rastreio": "BR123456789BR"
        }
        
        # CORRIGIDO: URL exata conforme o seu arquivo porteiro.py
        response = client.post("/api/porteiro/registrar-encomenda", json=payload, headers=headers)
        assert response.status_code in [200, 201]

def test_buscar_moradores_predio(client, app):
    """Garante que a rota que o porteiro usa para listar moradores no select funciona"""
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    with app.app_context():
        db.session.remove()
        porteiro = Usuario(nome="Porteiro Teste 2", email="porteiro2@teste.com", senha="123", perfil="Porteiro", is_active=True)
        db.session.add(porteiro)
        db.session.commit()
        
        token_porteiro = create_access_token(identity=str(porteiro.id), additional_claims={"perfil": "Porteiro"})
        headers = {"Authorization": f"Bearer {token_porteiro}"}
        
        # CORRIGIDO: URL exata passando o termo de busca '?query=Te' para passar da validação de tamanho mínimo
        response = client.get("/api/porteiro/buscar-moradores?query=Te", headers=headers)
        assert response.status_code == 200