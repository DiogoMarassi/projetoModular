from datetime import datetime

import matplotlib.pyplot as plt #Para a geracao de diagrama circular

from tests.data.gera_dados import tipos, categorias


import json
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ARQUIVO = os.path.join(BASE_DIR, "tests", "data", "lancamentos_testes.json")


def carregar_lancamentos():
    if os.path.exists(_ARQUIVO):
        with open(_ARQUIVO, 'r', encoding='utf-8') as f:
            lancamentos = json.load(f)
        # Converte datas de string para datetime
        for l in lancamentos:
            if isinstance(l["data"], str):
                l["data"] = datetime.fromisoformat(l["data"])
        return lancamentos
    return []


def calcular_saldo_antes(data_inicio):
    saldo = 0.0
    lancamentos = carregar_lancamentos()
    for l in lancamentos:
        if validar_lancamento(l) and l["data"] < data_inicio:
            if l["tipo"] == "receita":
                saldo += l["valor"]
            elif l["tipo"] == "despesa":
                saldo -= l["valor"]
    return saldo


def validar_lancamento(lancamento):
    return (
        lancamento.get("tipo") in tipos and
        lancamento.get("categoria") in categorias and
        isinstance(lancamento.get("valor"), (float, int)) and
        isinstance(lancamento.get("data"), datetime)
    )


def agrupar_por_categoria(lancamentos_especificos, tipo):
    categorias = {}
    total = 0.0
    for l in lancamentos_especificos:
        if l["tipo"] == tipo:
            cat = l["categoria"]
            categorias[cat] = categorias.get(cat, 0.0) + l["valor"]
            total += l["valor"]
    return categorias, total


def gerar_grafico_pizza_despesas(relatorio):
    despesas = relatorio["despesas"]
    categorias = [k for k in despesas if k != "total"]
    valores = [despesas[k] for k in categorias]

    if not categorias:
        print("Nenhuma despesa para exibir.")
        return

    plt.figure(figsize=(8, 6))
    plt.pie(valores, labels=categorias, autopct='%1.1f%%', startangle=140)
    plt.title("Distribuição de Despesas por Categoria")
    plt.axis('equal')  # para deixar o círculo "perfeito"
    plt.tight_layout()
    plt.show()


def gerar_relatorio_financeiro(periodo):
        
    """
    Generates a financial report summarizing income and expenses over a specified time period.

    This function is part of the `relatórios` module, which provides summaries of financial data
    for a given period and allows comparison between two years.

    Parameters
    ----------
    lancamentos: list of dict
        List containing randomly generated financial records.

    periodo : dict
        A dictionary specifying the time period to analyze. It must contain:
            - data_inicio (datetime): The start date of the period.
            - data_final (datetime): The end date of the period.

    Returns
    -------
    dict
        On success (HTTP 200):
            {
                "periodo": { "inicio": datetime, "fim": datetime },
                "saldoInicial": float,
                "receitas": {
                    "total": float,
                    "categorias": [ { "categoria": str, "valor": float } ]
                },
                "despesas": {
                    "total": float,
                    "categorias": [ { "categoria": str, "valor": float } ]
                },
                "saldoFinal": float,
                "variacao": float
            }

        On error (HTTP 400):
            { "Status": 400, "Content": "Invalid period." }

        On error (HTTP 404):
            { "Status": 404, "Content": "No records found." }

    Notes
    -----
    - Ensure that `data_inicio` is earlier than `data_final`.
    - This function does not perform database insertion; it only reads and summarizes data.
    """
    
    lancamentos = carregar_lancamentos()
    

    data_inicio = periodo.get("data_inicio")
    data_fim = periodo.get("data_final")

    # Erro 400: se as datas forem incoerentes
    if data_inicio > data_fim:
        return {"Status": 400, "Content": "Período inválido."}
    

    lancamentos_periodo = [
        l for l in lancamentos
        if validar_lancamento(l) and data_inicio <= l["data"] < data_fim
    ]


    # Erro 404: se nao tiver lancamento neste periodo
    if not lancamentos_periodo:
        return {"Status": 404, "Content": "Nenhum lançamento encontrado"}

    saldo_inicial = calcular_saldo_antes(data_inicio)
    receitas_por_cat, soma_receitas_periodo = agrupar_por_categoria(lancamentos_periodo, "receita")
    despesas_por_cat, soma_despesas_periodo = agrupar_por_categoria(lancamentos_periodo, "despesa")
    saldo_final = saldo_inicial + soma_receitas_periodo - soma_despesas_periodo
    variacao = saldo_final - saldo_inicial

    relatorio = {
        "periodo": {
            "inicio": data_inicio.strftime("%Y-%m-%d"),
            "fim": data_fim.strftime("%Y-%m-%d")},
        "saldoInicial": round(saldo_inicial, 2),
        "receitas": {"total": round(soma_receitas_periodo, 2), **receitas_por_cat},
        "despesas": {"total": round(soma_despesas_periodo, 2), **despesas_por_cat},
        "saldoFinal": round(saldo_final, 2),
        "variacao": round(variacao, 2)
    }

    return {"Status": 200, "Content": relatorio}




def categoria_maior_dif_despesa(relatorioano1, relatorioano2):
    categorias = set(relatorioano1["despesas"].keys()).union(relatorioano2["despesas"].keys())
    categorias.discard("total")

    categorias_dif = []
    categoria_maior_gasto = {"categoria": "NONE",
                "valorAno1": -1,
                "valorAno2": -1,
                "diferenca": -1}
    max_dif = -1

    for cat in categorias:
        valor1 = relatorioano1["despesas"].get(cat, 0)
        valor2 = relatorioano2["despesas"].get(cat, 0)
        diferenca = valor2 - valor1

        categorias_dif.append({
            "categoria": cat,
            "valorAno1": round(valor1, 2),
            "valorAno2": round(valor2, 2),
            "diferenca": round(diferenca, 2),
        })

        if diferenca > max_dif:
            print("TOTO")
            max_dif = diferenca
            categoria_maior_gasto = {
                "categoria": cat,
                "valorAno1": round(valor1, 2),
                "valorAno2": round(valor2, 2),
                "diferenca": round(diferenca, 2),
            }

    return categorias_dif, categoria_maior_gasto




def gerar_comparativo(ano1, ano2):

    """
    Compares financial data between two full years.

    This function analyzes financial summaries for two given years and returns a comparative report,
    including differences in income, expenses, final balance, and the category with the greatest variation.

    Parameters
    ----------
    lancamentos: list of dict
        List containing randomly generated financial records.
    ano1 : int
        The first year to analyze.
    ano2 : int
        The second year to analyze.
    console : bool, optional
        If True, prints the comparison to the console. Default is False.

    Returns
    -------
    dict
        On success (HTTP 200):
            {
                "ano1": {
                    "receitas": float,
                    "despesas": float,
                    "saldoFinal": float
                },
                "ano2": {
                    "receitas": float,
                    "despesas": float,
                    "saldoFinal": float
                },
                "diferencas": {
                    "receitas": float,
                    "despesas": float,
                    "saldoFinal": float
                },
                "categoriaComMaiorDiferenca": [
                    {
                        "categoria": str,
                        "valorPeriodo1": float,
                        "valorPeriodo2": float,
                        "diferenca": float
                    }
                ],
                "resumoTexto": str
            }

        On error (HTTP 400):
            { "Status": 400, "Content": "Invalid years or data." }

        On error (HTTP 404):
            { "Status": 404, "Content": "No records found for the selected years." }

    Notes
    -----
    - Years must be valid integers with available financial data.
    - The comparison includes aggregated totals and highlights the category with the largest change.
    """
    
    if ((ano1 < 0) or (ano2 < 0)):
        return {"Status": 400, "Content": "Ano inválido"}

    periodo_ano1 = {
        "data_inicio": datetime(ano1, 1, 1),
        "data_final": datetime(ano1+1, 1, 1)
    }
    periodo_ano2 = {
        "data_inicio": datetime(ano2, 1, 1),
        "data_final": datetime(ano2+1, 1, 1)
    }
    res1 = gerar_relatorio_financeiro(periodo_ano1)
    res2 = gerar_relatorio_financeiro(periodo_ano2)

    if (res1["Status"] == 400) or (res2["Status"] == 400):
        return {"Status": 400, "Content": "Período inválido."}
    if (res1["Status"] == 404) or (res2["Status"] == 404):
        return {"Status": 404, "Content": "Nenhum lançamento encontrado"}
    
    relatorioano1 = res1["Content"]
    relatorioano2 = res2["Content"]

    diferenca_receitas = relatorioano2["receitas"]["total"] - relatorioano1["receitas"]["total"]
    diferenca_despesas = relatorioano2["despesas"]["total"] - relatorioano1["despesas"]["total"]
    diferenca_saldoFinal = relatorioano2["saldoFinal"] - relatorioano1["saldoFinal"]

    gastos_por_categoria, cat_mais_gastos = categoria_maior_dif_despesa(relatorioano1, relatorioano2)
    print(cat_mais_gastos)

    resumo = (
    f"Em {ano2}, as receitas variaram em R$ {diferenca_receitas:.2f}, "
    f"as despesas em R$ {diferenca_despesas:.2f}, e o saldo final mudou em R$ {diferenca_saldoFinal:.2f}.\n"
)

    if (cat_mais_gastos["categoria"] == "NONE"):
        resumo += "Não houve aumento em nenhuma categoria de despesas.\n"
    else:
        resumo += (
            f"Cuidado com os gastos em '{cat_mais_gastos['categoria']}': "
            f"R$ {cat_mais_gastos['valorAno1']:.2f} em {ano1} contra "
            f"R$ {cat_mais_gastos['valorAno2']:.2f} em {ano2} "
            f"(+R$ {cat_mais_gastos['diferenca']:.2f}).\n"
        )

    resumo += "\nAumento das despesas:\n"
    aumentos = [item for item in gastos_por_categoria if item['diferenca'] > 0]
    if aumentos:
        for item in aumentos:
            resumo += f" - {item['categoria']}: +R$ {item['diferenca']:.2f}\n"
    else:
        resumo += "Nenhuma categoria teve aumento de despesas.\n"

    resumo += "\nRedução das despesas:\n"
    reducoes = [item for item in gastos_por_categoria if item['diferenca'] < 0]
    if reducoes:
        for item in reducoes:
            resumo += f" - {item['categoria']}: R$ {item['diferenca']:.2f}\n"
    else:
        resumo += "Nenhuma categoria teve redução de despesas.\n"



    comparativo = {
        "ano1": { "receitas": relatorioano1["receitas"],  "despesas": relatorioano1["despesas"], "saldoFinal": relatorioano1["saldoFinal"]},
        "ano2": { "receitas": relatorioano2["receitas"],  "despesas": relatorioano2["despesas"], "saldoFinal": relatorioano2["saldoFinal"]},
        "diferencas": { "receitas": diferenca_receitas, "despesas": diferenca_despesas, "saldoFinal": diferenca_saldoFinal},
        "categoriaComMaiorDiferenca": { "categoria": cat_mais_gastos['categoria'], "valorAno1": cat_mais_gastos['valorAno1'], "valorAno2": cat_mais_gastos['valorAno2'], "diferenca": cat_mais_gastos['diferenca']},
        "resumo": resumo,
    }
        
    return { "Status": 200, "Content": comparativo}