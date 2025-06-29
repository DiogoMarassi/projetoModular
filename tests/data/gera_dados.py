"""
INF1301 - Programação Modular
Responsável: Louis Pottier

Este programa permite iniciar um arquivo com dados gerados aleatoriamente
"""

import json
from datetime import datetime
from numpy import random

import os

# Categorias e tipos possíveis
from config import categorias, tipos, arquivo_final_dados

_proximo_id = 1

# Passeio nos arquivos (até encontrar a pasta de testes)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ARQUIVO = os.path.join(BASE_DIR, arquivo_final_dados)


def gerar_lancamentos(quantidade=50, anos=(2020, 2024)):
    """
    Gerar aleatoriamente dados de lancamentos

    Parameters
    ----------
    quantidade: int
        Número de lancamentos a serem gerados

    anos : tuple
        Intervalo para as datas dos lancamentos

    Returns
    -------
    Dict
        {
        "lancamentos": List of dict
            [
                {
                    "id": int,
                    "descricao": str,
                    "valor": float,
                    "data": datatime,
                    "tipo": str,
                    "categoria": str
                }, ...
            ],
        "proximo_id": int
        }

    Notes
    -----
    Os campos 'tipo' e 'categoria' devem fazer parte das listas validas presentes no diretório config
    """

    global _proximo_id
    lancamentos = []

    for i in range(1, quantidade+1):
        ano = random.randint(anos[0], anos[1])
        mes = random.randint(1, 12)
        dia = random.randint(1, 28)
        tipo = random.choice(tipos)
        valor = round(random.uniform(1000, 5000), 2) if tipo == 'receita' else round(random.uniform(10, 500), 2)
        categoria = random.choice(categorias)
        descricao = f"Lançamento {i}"

        lancamento = {
            "id": _proximo_id,
            "descricao": descricao,
            "valor": valor,
            "data": datetime(ano, mes, dia).isoformat(),  # transforma para string ISO
            "tipo": tipo,
            "categoria": categoria
        }

        lancamentos.append(lancamento)
        _proximo_id += 1

    return lancamentos

def _salvar_dados():
    """
    Salva os dados da memória para o arquivo JSON especificado
    """

    lancamentos = gerar_lancamentos()

    dados_para_salvar = {
        'lancamentos': [],
        'proximo_id': _proximo_id
    }

    # Converte datetime para string para serialização JSON
    for lancamento in lancamentos:
        lancamento_copy = lancamento.copy()
        if isinstance(lancamento_copy['data'], datetime):
            lancamento_copy['data'] = lancamento_copy['data'].isoformat()
        dados_para_salvar['lancamentos'].append(lancamento_copy)
    
    try:
        with open(_ARQUIVO, 'w', encoding='utf-8') as arquivo:
            json.dump(dados_para_salvar, arquivo, indent=2, ensure_ascii=False)
    except IOError:
        # Em caso de erro ao salvar, continua com dados em memória
        pass


# Se rodar direto o script, gera e salva
if __name__ == "__main__":
    _salvar_dados()