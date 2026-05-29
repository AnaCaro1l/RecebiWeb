import pytest

def test_consultar_encomendas_sem_autenticacao(client):
    """Valida bloqueio de segurança na rota do morador"""
    resposta = client.get("/api/morador/encomendas")
    assert resposta.status_code == 401

def test_filtrar_encomendas_status_invalido(client):
    """Garante que parâmetros inválidos barram ou não quebram o app"""
    resposta = client.get("/api/morador/encomendas?status=Inexistente")
    assert resposta.status_code == 401  