import json
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Dados encapsulados (não são exportados diretamente)
_notificacoes = []

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ARQUIVO = os.path.join(BASE_DIR, "data", "notificacoes.json")

def setArquivoPersistencia(caminho):
    """
    Permite alterar o caminho do arquivo de persistência (útil para testes).
    """
    global _ARQUIVO
    _ARQUIVO = caminho
    _carregar_notificacoes()

def resetarNotificacoes():
    """
    Função de uso interno ou para testes.
    Remove todas as notificações da memória e do arquivo persistente.
    """
    global _notificacoes
    _notificacoes = []
    _salvar_notificacoes()

# Função interna para carregar dados do arquivo
def _carregar_notificacoes():
    global _notificacoes
    if os.path.exists(_ARQUIVO):
        with open(_ARQUIVO, 'r', encoding='utf-8') as f:
            _notificacoes = json.load(f)
    else:
        _notificacoes = []

# Função interna para salvar dados no arquivo
def _salvar_notificacoes():
    with open(_ARQUIVO, 'w', encoding='utf-8') as f:
        json.dump(_notificacoes, f, ensure_ascii=False, indent=4, default=str)

# Inicializa carregando as notificações na abertura do módulo
_carregar_notificacoes()


# Função de acesso: Listar notificações
def listarNotificacoes():
    """
    Retorna a lista de notificações armazenadas.
    """
    if _notificacoes:
        return {"Status": 200, "Content": _notificacoes}
    else:
        return {"Status": 404, "Content": "Usuário não encontrado"}


# Função de acesso: Salvar uma nova notificação local
def salvarNotificacao(conteudo):
    """
    Salva uma notificação localmente com data e hora atual.
    """
    if not conteudo or not isinstance(conteudo, str) or conteudo.strip() == "":
        return {"Status": 404, "Content": "Usuário não encontrado"}

    nova = {
        "data": datetime.now().isoformat(timespec='seconds'),
        "conteudo": conteudo.strip()
    }
    _notificacoes.append(nova)
    _salvar_notificacoes()
    return {"Status": 200, "Content": _notificacoes}


# Função de acesso: Enviar notificação (simula envio para Telegram)
def enviarNotificacao(chatId, conteudo):
    """
    Envia uma notificação real para o Telegram usando a Telegram Bot API.
    Além disso, salva a notificação localmente.
    """
    if not isinstance(chatId, int) or chatId <= 0:
        return {"Status": 404, "Content": "Chat não encontrado"}

    if not conteudo or not isinstance(conteudo, str) or conteudo.strip() == "":
        return {"Status": 404, "Content": "Chat não encontrado"}

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chatId,
        "text": conteudo
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Levanta erro para respostas como 400, 404, etc.

        salvarNotificacao(conteudo)  # Sempre salva localmente também

        return {"Status": 200, "Content": "Mensagem enviada com sucesso"}
    
    except requests.exceptions.HTTPError as e:
        return {"Status": 404, "Content": "Chat não encontrado"}
    except Exception as e:
        return {"Status": 500, "Content": f"Erro ao enviar mensagem: {str(e)}"}


# Garanta que as notificações sejam salvas ao finalizar a execução
import atexit
atexit.register(_salvar_notificacoes)
