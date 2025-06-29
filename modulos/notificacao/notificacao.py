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
import atexit

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ARQUIVO_NOTIFICACOES = os.path.join(_BASE_DIR, "data", "notificacoes.json")

# Dados encapsulados - lista de lançamentos em memória

load_dotenv()
_TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

_notificacoes: List[Dict[str, str]] = []

# Funções internas

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

# Persistência entre execuções 

# Carrega ao importar
_carregar_notificacoes()

# Persistencia no encerramento
atexit.register(_salvar_notificacoes)

# Funções auxiliares

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


# Funções de acesso (públicas)

def listarNotificacoes() -> Dict[str, Union[int, str, List[Dict[str, str]]]]:
    """
    Retorna todas as notificações armazenadas.

    Returns:
        dict: {"Status": 200, "Content": lista} ou {"Status": 404, "Content": 'Erro ao acessar notificações'}
    """
    print(_notificacoes)
    if _notificacoes:
        return {"Status": 200, "Content": _notificacoes}
    else:
        return {"Status": 404, "Content": "Erro ao acessar notificações"}

def salvarNotificacao(conteudo: str) -> Dict[str, Union[int, str, List[Dict[str, str]]]]:
    """
    Adiciona uma notificação com data/hora atual à memória.

    Args:
        conteudo (str): Texto da notificação

    Returns:
        dict: {"Status": 200, "Content": lista atualizada} ou {"Status": 404, ...}
    """
    print("Entrou em salvarNotificacao")
    if not conteudo or not isinstance(conteudo, str) or conteudo.strip() == "":
        return {"Status": 404, "Content": "Usuário não encontrado"}
    
    nova = {
        "data": datetime.now().isoformat(timespec='seconds'),
        "conteudo": conteudo.strip()
    }
    print(nova)
    _notificacoes.append(nova)
    print(_notificacoes)
    return {"Status": 200, "Content": _notificacoes}

def filtrarNotificacoesPorPeriodo(data_inicio: str, data_fim: str) -> Dict[str, Union[int, str, List[Dict[str, str]]]]:
    """
    Filtra notificações armazenadas entre duas datas (inclusive), considerando apenas dia/mês/ano.

    Args:
        data_inicio (str): Data inicial no formato DD/MM/AAAA
        data_fim (str): Data final no formato DD/MM/AAAA

    Returns:
        dict: {"Status": 200, "Content": [notificacoes]} ou {"Status": 400/404, "Content": msg}
    """
    try:
        inicio = datetime.strptime(data_inicio, "%d/%m/%Y").date()
        fim = datetime.strptime(data_fim, "%d/%m/%Y").date()
    except ValueError:
        return {"Status": 400, "Content": "Formato de data inválido. Use DD/MM/AAAA."}

    if inicio > fim:
        return {"Status": 400, "Content": "Data inicial maior que data final."}

    notificacoes_filtradas = []
    for n in _notificacoes:
        try:
            data_notificacao = datetime.fromisoformat(n["data"]).date()
            if inicio <= data_notificacao <= fim:
                notificacoes_filtradas.append(n)
        except Exception:
            continue  # ignora notificações mal formatadas

    if notificacoes_filtradas:
        return {"Status": 200, "Content": notificacoes_filtradas}
    else:
        return {"Status": 404, "Content": "Nenhuma notificação no período."}
    
def enviarNotificacao(chatId: int, conteudo: str) -> Dict[str, Union[int, str]]:
    """
    Envia uma notificação para o Telegram via API e armazena localmente.

    Args:
        chatId (int): ID do usuário no Telegram
        conteudo (str): Texto da mensagem

    Returns:
        dict: {"Status": 200, "Content": "Mensagem enviada com sucesso"} ou erro
    """
    global _notificacoes
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
