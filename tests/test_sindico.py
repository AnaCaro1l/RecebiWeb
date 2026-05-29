import pytest
from recebi.models.usuario import Usuario
from recebi.ext.db import db

def test_listar_usuarios_sem_autenticacao(client):
    """Garante que a rota bloqueia acessos sem Token JWT"""
    resposta = client.get("/api/sindico/usuarios")
    assert resposta.status_code == 401

def test_listar_usuarios_vazio(client, auth_headers):
    """Testa o retorno da paginação quando houver apenas o síndico cadastrado"""
    resposta = client.get("/api/sindico/usuarios?page=1", headers=auth_headers)
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert "usuarios" in dados
    assert "paginacao" in dados
    assert len(dados["usuarios"]) == 1  

def test_criar_usuario_via_sindico(client, auth_headers):
    """Testa a criação bem-sucedida de um novo morador"""
    novo_user_payload = {
        "nome": "Lucas Morador",
        "email": "lucas@teste.com",
        "senha": "password123",
        "tipoUsuario": "Morador",
        "apartamento": "401"
    }
    resposta = client.post("/api/sindico/criar", json=novo_user_payload, headers=auth_headers)
    assert resposta.status_code == 201
    assert resposta.get_json()["usuario"]["Nome"] == "Lucas Morador"

def test_filtrar_usuarios_por_nome(client, auth_headers):
    """Testa a busca textual e parcial do filtro por nome"""
    resposta = client.get("/api/sindico/usuarios?nome=Lucas", headers=auth_headers)
    assert resposta.status_code == 200
    dados = resposta.get_json()
    for u in dados["usuarios"]:
        assert "Lucas" in u["Nome"]

def test_consultar_logs_auditoria(client, auth_headers):
    """Testa o retorno estruturado e paginado dos logs de auditoria"""
    resposta = client.get("/api/sindico/logs?page=1", headers=auth_headers)
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert "logs" in dados
    assert "paginacao" in dados