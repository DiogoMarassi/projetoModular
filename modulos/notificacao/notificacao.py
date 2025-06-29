"""
Módulo Notificações
INF1301 - Programação Modular
Responsável: Diogo Marassi

Este módulo relatórios permite:
- Gerenciar e armazenar notificações locais
- Enviar mensagens via Telegram usando chatId
- Persistir notificações em arquivo JSON (apenas no encerramento da aplicação)
"""


import json
import os
import requests
from datetime import datetime
from typing import List, Dict, Union
from dotenv import load_dotenv

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ARQUIVO_NOTIFICACOES = os.path.join(_BASE_DIR, "data", "notificacoes.json")

# ----------------------
# Variáveis privadas
# ----------------------
load_dotenv()
_TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

_notificacoes: List[Dict[str, str]] = []

# ----------------------
# Funções internas
# ----------------------

def _carregar_notificacoes() -> None:
    """
    Carrega notificações do JSON para a memória (executado na importação).
    """
    global _notificacoes
    if os.path.exists(_ARQUIVO_NOTIFICACOES):
        with open(_ARQUIVO_NOTIFICACOES, 'r', encoding='utf-8') as f:
            _notificacoes = json.load(f)
    else:
        _notificacoes = []

def _salvar_notificacoes() -> None:
    """
    Salva notificações da memória no arquivo JSON (executado ao encerrar).
    """
    with open(_ARQUIVO_NOTIFICACOES, 'w', encoding='utf-8') as f:
        json.dump(_notificacoes, f, ensure_ascii=False, indent=4, default=str)

# Carrega ao importar
_carregar_notificacoes()

# ----------------------
# Funções auxiliares (testes)
# ----------------------

def setArquivoPersistencia(caminho: str) -> None:
    """
    Altera o caminho do arquivo de persistência (para testes).
    """
    global _ARQUIVO_NOTIFICACOES
    _ARQUIVO_NOTIFICACOES = caminho
    _carregar_notificacoes()

def resetarNotificacoes() -> None:
    """
    Limpa todas as notificações em memória (para testes).
    """
    global _notificacoes
    _notificacoes = []

# ----------------------
# Funções de acesso (públicas)
# ----------------------

def listarNotificacoes() -> Dict[str, Union[int, str, List[Dict[str, str]]]]:
    """
    Retorna todas as notificações armazenadas.

    Returns:
        dict: {"Status": 200, "Content": lista} ou {"Status": 404, "Content": "Usuário não encontrado"}
    """
    if _notificacoes:
        return {"Status": 200, "Content": _notificacoes}
    else:
        return {"Status": 404, "Content": "Usuário não encontrado"}

def salvarNotificacao(conteudo: str) -> Dict[str, Union[int, str, List[Dict[str, str]]]]:
    """
    Adiciona uma notificação com data/hora atual à memória.

    Args:
        conteudo (str): Texto da notificação

    Returns:
        dict: {"Status": 200, "Content": lista atualizada} ou {"Status": 404, ...}
    """
    if not conteudo or not isinstance(conteudo, str) or conteudo.strip() == "":
        return {"Status": 404, "Content": "Usuário não encontrado"}

    nova = {
        "data": datetime.now().isoformat(timespec='seconds'),
        "conteudo": conteudo.strip()
    }
    _notificacoes.append(nova)
    return {"Status": 200, "Content": _notificacoes}

def enviarNotificacao(chatId: int, conteudo: str) -> Dict[str, Union[int, str]]:
    """
    Envia uma notificação para o Telegram via API e armazena localmente.

    Args:
        chatId (int): ID do usuário no Telegram
        conteudo (str): Texto da mensagem

    Returns:
        dict: {"Status": 200, "Content": "Mensagem enviada com sucesso"} ou erro
    """
    if not isinstance(chatId, int) or chatId <= 0:
        return {"Status": 404, "Content": "Chat não encontrado"}

    if not conteudo or not isinstance(conteudo, str) or conteudo.strip() == "":
        return {"Status": 404, "Content": "Chat não encontrado"}

    url = f"https://api.telegram.org/bot{_TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chatId, "text": conteudo}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        salvarNotificacao(conteudo)  # apenas em memória
        return {"Status": 200, "Content": "Mensagem enviada com sucesso"}
    except requests.exceptions.HTTPError:
        return {"Status": 404, "Content": "Chat não encontrado"}
    except Exception as e:
        return {"Status": 500, "Content": f"Erro ao enviar mensagem: {str(e)}"}

# ----------------------
# Persistência no encerramento
# ----------------------

import atexit
atexit.register(_salvar_notificacoes)

# ----------------------
# Exportações explícitas
# ----------------------

__all__ = [
    "listarNotificacoes",
    "salvarNotificacao",
    "enviarNotificacao",
    "setArquivoPersistencia",
    "resetarNotificacoes",
]
