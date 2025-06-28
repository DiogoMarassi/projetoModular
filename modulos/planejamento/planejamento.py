"""
Módulo de Planejamento
Responsável pelo módulo: Pedro Basto
Módulo responsavel por:
- Calcular um planejamento automático com base no salário do usuário que pode vir de um input ou do lançamento mais recente
- Permitir edição manual do usuário para alterar os valores padrão
- Persistir o planejamento para um arquivo JSON
"""

import os
import json
from modulos.lancamento import listarLancamentos

# Encapsulamento - Lista das funções disponibilizadas pelo módulo
__all__ = [
    "calculaDivisaoGastos",
    "editarDivisaoGastos",
    "obterDivisaoSalva",
    "obterSalarioMaisRecente",
    "calculaDivisaoDoUltimoSalario"
]

# Dados encapsulados - caminho do arquivo e percentuais padrão com referência a classe média do RJ
_percentuais_padrao = { 
    "moradia": 0.30,
    "alimentacao": 0.20,
    "transporte": 0.05,
    "saude": 0.10,
    "educacao": 0.10,
    "lazer": 0.10,
    "guardar": 0.15
}

_arquivo_dados = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../data/planejamento.json")
)


def calculaDivisaoGastos(salarioBaseUsuario):
    """
    Calcula a divisão de gastos com base no salário informado. 
    Salário deve ser maior do que o salário mínimo brasileiro e do tipo int ou float
    """
    if not isinstance(salarioBaseUsuario, (int, float)) or salarioBaseUsuario <= 1630:
        return {"Error": 400, "Content": "Salário Inválido"}

    divisao = {
        categoria: round(salarioBaseUsuario * percentual, 2)
        for categoria, percentual in _percentuais_padrao.items()
    }

    resultado = {
        "salario": round(salarioBaseUsuario, 2),
        "divisao": divisao
    }

    try:
        with open(_arquivo_dados, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=4, ensure_ascii=False)
    except Exception as e:
        return {"Error": 500, "Content": f"Erro ao salvar arquivo: {str(e)}"}

    return {"Success": 200, "Content": resultado}


def editarDivisaoGastos(novaDivisaoGastos):
    """
    Edita manualmente a divisão de gastos.
    """
    if not isinstance(novaDivisaoGastos, dict):
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    salario = novaDivisaoGastos.get("salario")
    divisao = novaDivisaoGastos.get("divisao")

    if salario <= 1630:
        return {"Error": 400, "Content": "Salário inválido"}

    if not salario or not divisao or not isinstance(divisao, dict):
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    soma = round(sum(divisao.values()), 2)
    if round(salario, 2) != soma or any(v < 0 for v in divisao.values()):
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    try:
        with open(_arquivo_dados, "w", encoding="utf-8") as f:
            json.dump(novaDivisaoGastos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        return {"Error": 500, "Content": f"Erro ao salvar arquivo: {str(e)}"}

    return {"Success": 200, "Content": novaDivisaoGastos}


def obterDivisaoSalva():
    """
    Retorna a divisão salva no arquivo JSON.
    """
    if not os.path.exists(_arquivo_dados):
        return {"Error": 404, "Content": "Divisão não encontrada"}

    try:
        with open(_arquivo_dados, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return {"Success": 200, "Content": dados}
    except Exception as e:
        return {"Error": 500, "Content": f"Erro ao ler arquivo: {str(e)}"}


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