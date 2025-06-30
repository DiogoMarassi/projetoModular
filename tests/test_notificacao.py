import pytest
import os
from modulos.notificacao import *

from dotenv import load_dotenv


# Setup de ambiente
load_dotenv()
CHAT_ID_VALIDO = int(os.getenv("TELEGRAM_CHAT_ID", "0"))  # Pode ser mockado
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_TESTE = os.path.join(BASE_DIR, "tests", "data", "notificacoes.json")

# Fixture para preparar ambiente limpo
@pytest.fixture(autouse=True)
def ambiente_limpo():
    setArquivoPersistencia(ARQUIVO_TESTE)
    resetarNotificacoes()
    if os.path.exists(ARQUIVO_TESTE):
        os.remove(ARQUIVO_TESTE)
    yield
    if os.path.exists(ARQUIVO_TESTE):
        os.remove(ARQUIVO_TESTE)


# Casos de teste
def test_listar_notificacoes_vazio():
    response = listarNotificacoes()
    assert response["Status"] == 404
    assert response["Content"] == 'Erro ao acessar notificações'

def test_salvar_notificacao_valida():
    response = salvarNotificacao("Gasto ultrapassou limite!")
    assert response["Status"] == 200
    assert isinstance(response["Content"], list)
    assert len(response["Content"]) == 1
    assert "Gasto ultrapassou limite!" in response["Content"][0]["conteudo"]

@pytest.mark.parametrize("conteudo_invalido", ["", None, "   "])
def test_salvar_notificacao_invalida(conteudo_invalido):
    response = salvarNotificacao(conteudo_invalido)
    assert response["Status"] == 404
    assert response["Content"] == "Usuário não encontrado"

def test_listar_notificacoes_apos_salvar():
    salvarNotificacao("Notificação 1")
    salvarNotificacao("Notificação 2")
    response = listarNotificacoes()
    assert response["Status"] == 200
    assert isinstance(response["Content"], list)
    assert len(response["Content"]) == 2

def test_enviar_notificacao_valida(monkeypatch):
    def mock_post(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self): pass
        return MockResponse()
    monkeypatch.setattr("requests.post", mock_post)
    response = enviarNotificacao(CHAT_ID_VALIDO, "Saldo abaixo do esperado.")
    assert response["Status"] == 200
    assert response["Content"] == "Mensagem enviada com sucesso"

@pytest.mark.parametrize("chat_invalido", [None, -5, 0, "abc"])
def test_enviar_notificacao_chat_invalido(chat_invalido):
    response = enviarNotificacao(chat_invalido, "Mensagem")
    assert response["Status"] == 404
    assert response["Content"] == "Chat não encontrado"

@pytest.mark.parametrize("mensagem_invalida", ["", None, "   "])
def test_enviar_notificacao_conteudo_invalido(mensagem_invalida):
    response = enviarNotificacao(123456, mensagem_invalida)
    assert response["Status"] == 404
    assert response["Content"] == "Chat não encontrado"