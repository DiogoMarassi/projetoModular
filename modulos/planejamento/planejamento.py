# modulos/planejamento/planejamento.py

import json
import os

CAMINHO_ARQUIVO = os.path.join("data", "planejamento.json")

PERCENTUAIS_PADRAO = {
    "moradia": 0.30,
    "alimentacao": 0.20,
    "transporte": 0.15,
    "lazer": 0.10,
    "saude": 0.10,
    "educacao": 0.05,
    "poupanca": 0.10,
}

def calculaDivisaoGastos(salarioBaseUsuario):
    if not isinstance(salarioBaseUsuario, (int, float)) or salarioBaseUsuario <= 0:
        return {"Error": 400, "Content": "Salário Inválido"}

    divisao = {
        categoria: round(salarioBaseUsuario * percentual, 2)
        for categoria, percentual in PERCENTUAIS_PADRAO.items()
    }

    resultado = {
        "salario": round(salarioBaseUsuario, 2),
        "divisao": divisao
    }

    try:
        with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=4, ensure_ascii=False)
    except Exception as e:
        return {"Error": 500, "Content": f"Erro ao salvar arquivo: {str(e)}"}

    return {"Success": 200, "Content": resultado}


def editarDivisaoGastos(novaDivisaoGastos):
    if not isinstance(novaDivisaoGastos, dict):
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    salario = novaDivisaoGastos.get("salario")
    divisao = novaDivisaoGastos.get("divisao")

    if not salario or not divisao or not isinstance(divisao, dict):
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    soma = round(sum(divisao.values()), 2)
    if round(salario, 2) != soma or any(v < 0 for v in divisao.values()):
        return {"Error": 400, "Content": "Nova divisão de gastos inválida"}

    try:
        with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(novaDivisaoGastos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        return {"Error": 500, "Content": f"Erro ao salvar arquivo: {str(e)}"}

    return {"Success": 200, "Content": novaDivisaoGastos}


def obterDivisaoSalva():
    if not os.path.exists(CAMINHO_ARQUIVO):
        return {"Error": 404, "Content": "Divisão não encontrada"}

    try:
        with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return {"Success": 200, "Content": dados}
    except Exception as e:
        return {"Error": 500, "Content": f"Erro ao ler arquivo: {str(e)}"}
