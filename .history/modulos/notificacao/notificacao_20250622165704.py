import json
from datetime import datetime
import os

# Dados encapsulados (não são exportados diretamente)
_notificacoes = []

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ARQUIVO = os.path.join(BASE_DIR, "data", "notificacoes.json")


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
        return {"Success": 200, "Content": _notificacoes}
    else:
        return {"Error": 404, "Content": "Usuário não encontrado"}

# Função de acesso: Salvar uma nova notificação local
def salvarNotificacao(conteudo):
    """
    Salva uma notificação localmente com data e hora atual.
    """
    if not conteudo or not isinstance(conteudo, str) or conteudo.strip() == "":
        return {"Error": 404, "Content": "Usuário não encontrado"}

    nova = {
        "data": datetime.now().isoformat(timespec='seconds'),
        "conteudo": conteudo.strip()
    }
    _notificacoes.append(nova)
    _salvar_notificacoes()
    return {"Success": 200, "Content": _notificacoes}

# Função de acesso: Enviar notificação (simula envio para Telegram)
def enviarNotificacao(chatId, conteudo):
    """
    Simula o envio de uma notificação para o Telegram (mock).
    Além disso, salva a notificação localmente.
    """
    if not isinstance(chatId, int) or chatId <= 0:
        return {"Error": 404, "Content": "Chat não encontrado"}

    if not conteudo or not isinstance(conteudo, str) or conteudo.strip() == "":
        return {"Error": 404, "Content": "Chat não encontrado"}

    # Simula envio para Telegram (mock)
    mensagem = f"[Telegram] Mensagem para {chatId}: {conteudo}"
    print(mensagem)  # Simula o envio (no real seria uma API do Telegram)

    # Salva também localmente
    salvarNotificacao(conteudo)

    return {"Success": 200, "Content": "Mensagem enviada com sucesso"}


# Garanta que as notificações sejam salvas ao finalizar a execução
import atexit
atexit.register(_salvar_notificacoes)
