import pytest
import os
from modulos.notificacao.notificacao import listarNotificacoes, salvarNotificacao, enviarNotificacao, setArquivoPersistencia, resetarNotificacoes
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_TESTE = os.path.join(BASE_DIR, "tests", "data", "notificacoes.json")

setArquivoPersistencia(ARQUIVO_TESTE)
resetarNotificacoes()

@pytest.fixture(autouse=True)
def limpar_arquivo():
    if os.path.exists(ARQUIVO_TESTE):
        print(f"Removendo arquivo de teste: {ARQUIVO_TESTE}")
        os.remove(ARQUIVO_TESTE)
    yield
    if os.path.exists(ARQUIVO_TESTE):
        print(f"Removendo arquivo de teste após os testes: {ARQUIVO_TESTE}")
        os.remove(ARQUIVO_TESTE)

# Teste listar notificações sem dados (espera erro 404)
def test_listar_notificacoes_sem_dados():
    response = listarNotificacoes()
    assert response["Error"] == 404
    assert response["Content"] == "Usuário não encontrado"

# Teste salvar notificação com sucesso
def test_salvar_notificacao_sucesso():
    response = salvarNotificacao("Despesa ultrapassou limite")
    assert response["Success"] == 200
    assert isinstance(response["Content"], list)
    assert any("Despesa ultrapassou limite" in n["conteudo"] for n in response["Content"])

# Teste salvar notificação com conteúdo inválido (espera erro 404)
@pytest.mark.parametrize("conteudo", ["", None, "   "])
def test_salvar_notificacao_conteudo_invalido(conteudo):
    response = salvarNotificacao(conteudo)
    assert response["Error"] == 404
    assert response["Content"] == "Usuário não encontrado"

# Teste listar notificações após salvar
def test_listar_notificacoes_apos_salvar():
    salvarNotificacao("Nova notificação")
    response = listarNotificacoes()
    assert response["Success"] == 200
    assert isinstance(response["Content"], list)
    assert any("Nova notificação" in n["conteudo"] for n in response["Content"])

# Teste enviar notificação com sucesso (mock do Telegram)
def test_enviar_notificacao_sucesso():
    response = enviarNotificacao(CHAT_ID, "Seu saldo está baixo")
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(response)
    assert response["Success"] == 200
    assert response["Content"] == "Mensagem enviada com sucesso"

# Teste enviar notificação com chatId inválido (espera erro 404)
@pytest.mark.parametrize("chatId", [None, -1, 0, "abc"])
def test_enviar_notificacao_chat_invalido(CHAT_ID):
    response = enviarNotificacao(CHAT_ID, "Teste")
    assert response["Error"] == 404
    assert response["Content"] == "Chat não encontrado"

# Teste enviar notificação com mensagem inválida (espera erro 404)
@pytest.mark.parametrize("conteudo", ["", None, "   "])
def test_enviar_notificacao_conteudo_invalido(conteudo):
    response = enviarNotificacao(123, conteudo)
    assert response["Error"] == 404
    assert response["Content"] == "Chat não encontrado"
