"""
Módulo Planejamento Financeiro
INF1301 - Programação Modular
Responsável: Pedro Basto

Este módulo permite:
- Calcular um planejamento automático com base no salário do usuário que pode vir de um input ou do lançamento mais recente
- Permitir edição manual do usuário para alterar os valores padrão
- Persistir o planejamento para um arquivo JSON
"""

import os
import json
from modulos.lancamento import listarLancamentos
from typing import Dict
import atexit

# Dados encapsulados
_percentuais_padrao: Dict[str, float] = { 
    "moradia": 0.30,
    "alimentacao": 0.20,
    "transporte": 0.05,
    "saude": 0.10,
    "educacao": 0.10,
    "lazer": 0.10,
    "guardar": 0.15
}

_dados_planejamento: Dict[str, object] = {}

_arquivo_dados = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/planejamento.json")
)


def _carregar_dados():
    global _dados_planejamento
    if os.path.exists(_arquivo_dados):
        try:
            with open(_arquivo_dados, "r", encoding="utf-8") as f:
                _dados_planejamento = json.load(f)
        except Exception:
            _dados_planejamento = {}


def _salvar_dados():
    try:
        with open(_arquivo_dados, "w", encoding="utf-8") as f:
            json.dump(_dados_planejamento, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


_carregar_dados()
atexit.register(_salvar_dados)


def calculaDivisaoGastos(salarioBaseUsuario):
    """
    Calcula a divisão de gastos com base no salário informado. 
    Salário deve ser maior do que o salário mínimo brasileiro e do tipo int ou float
    """
    global _dados_planejamento

    if not isinstance(salarioBaseUsuario, (int, float)) or salarioBaseUsuario <= 1630:
        return {"Error": 400, "Content": "Salário Inválido"}

    divisao = {
        categoria: round(salarioBaseUsuario * percentual, 2)
        for categoria, percentual in _percentuais_padrao.items()
    }

    _dados_planejamento = {
        "salario": round(salarioBaseUsuario, 2),
        "divisao": divisao
    }

    return {"Success": 200, "Content": _dados_planejamento}


def editarDivisaoGastos(novaDivisaoGastos):
    """
    Edita manualmente a divisão de gastos.
    """
    global _dados_planejamento

    if not isinstance(novaDivisaoGastos, dict):
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    salario = novaDivisaoGastos.get("salario")
    divisao = novaDivisaoGastos.get("divisao")

    if not salario or not divisao or not isinstance(divisao, dict):
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    if salario <= 1630 or any(v < 0 for v in divisao.values()):
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    soma = round(sum(divisao.values()), 2)
    if round(salario, 2) != soma:
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    _dados_planejamento = novaDivisaoGastos

    return {"Success": 200, "Content": _dados_planejamento}


def obterDivisaoSalva():
    """
    Retorna a divisão salva atualmente em memória.
    """
    if not _dados_planejamento:
        return {"Error": 404, "Content": "Divisão não encontrada"}

    return {"Success": 200, "Content": _dados_planejamento}


def obterSalarioMaisRecente():
    """
    Usa listarLancamentos() para obter o salário mais recente.
    """
    response = listarLancamentos({
        "tipo": "receita",
        "categoria": "Salario"
    })

    if "Error" in response:
        return {"Error": 404, "Content": "Nenhum salário encontrado."}

    # Já vem ordenado por data decrescente
    salario_mais_recente = response["Content"][0]
    valor = salario_mais_recente["valor"]

    return {"Success": 200, "Content": valor}


def calculaDivisaoDoUltimoSalario():
    """
    Calcula divisão usando o salário mais recente dos lançamentos.
    """
    salario_response = obterSalarioMaisRecente()
    if "Error" in salario_response:
        return salario_response

    salario = salario_response["Content"]
    return calculaDivisaoGastos(salario)
