from datetime import datetime
import matplotlib.pyplot as plt #Para a geracao de diagrama circular
from tests.data.gera_dados import tipos, categorias

import json
from datetime import datetime
import os
from fpdf import FPDF

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


def agrupar_por_categoria(lancamentos_periodo, tipo):
    categorias = {}
    total = 0.0
    for l in lancamentos_periodo:
        if l["tipo"] == tipo:
            cat = l["categoria"]
            categorias[cat] = categorias.get(cat, 0.0) + round(l["valor"], 2)
            total += round(l["valor"], 2)
    return categorias, total


def gerar_grafico_pizza_despesas(relatorio):
    despesas = relatorio["Content"]["despesas"]
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


def converter_PDF(resumo, nome_arquivo):
    pdf = FPDF()
    pdf.add_page()

    # Fonte padrão: Arial, tamanho 12
    pdf.set_font("Arial", size=12)

    # Divide o texto em linhas e escreve uma por uma
    for linha in resumo.strip().split('\n'):
        pdf.multi_cell(0, 10, linha)

    # Salva o PDF
    pdf.output(nome_arquivo)
    print(f"PDF salvo como '{nome_arquivo}'")



def gerar_relatorio_financeiro(periodo, PDF=False):
        
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
                "resumo": str
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

    resumo = (
        f"Saldo inicial no dia {data_inicio.strftime('%Y-%m-%d')}: R$ {round(saldo_inicial,2)}\n"
        f"Saldo final no dia {data_fim.strftime('%Y-%m-%d')}: R$ {round(saldo_final,2)}\n"
        f"Total de receitas nesse período: R$ {round(soma_receitas_periodo, 2)}\n"
        f"Total de despesas nesse período: R$ {round(soma_despesas_periodo, 2)}\n"
        f"Variação do saldo: R$ {round(variacao, 2)}\n"
        )


    relatorio = {
        "periodo": {
            "inicio": data_inicio.strftime("%Y-%m-%d"),
            "fim": data_fim.strftime("%Y-%m-%d")},
        "saldoInicial": round(saldo_inicial, 2),
        "receitas": {"total": round(soma_receitas_periodo, 2), **receitas_por_cat},
        "despesas": {"total": round(soma_despesas_periodo, 2), **despesas_por_cat},
        "saldoFinal": round(saldo_final, 2),
        "variacao": round(variacao, 2),
        "resumo": resumo
    }

    if PDF:
        converter_PDF(resumo, "./tests/data/relatorios_pdf/relatorio.pdf")
    

    return {"Status": 200, "Content": relatorio}


def categoria_maior_dif_despesa(relatorioano1, relatorioano2):
    # Unir todas as categorias presentes em receitas e despesas dos dois anos
    categorias = (
        set(relatorioano1.get("despesas", {}).keys()) |
        set(relatorioano2.get("despesas", {}).keys()) |
        set(relatorioano1.get("receitas", {}).keys()) |
        set(relatorioano2.get("receitas", {}).keys())
    )
    categorias.discard("total")

    print("Categorias: ", categorias, "\n")

    lista_dif_por_cat = []
    categoria_maior_gasto = {
        "categoria": None,
        "valorAno1": 0,
        "valorAno2": 0,
        "variacao": float('+inf')
        }
    categoria_maior_ganho = {
        "categoria": None,
        "valorAno1": 0,
        "valorAno2": 0,
        "variacao": float('-inf')
        }
    

    for cat in categorias:
        # Obtém os valores de despesas e receitas para os dois anos
        despesa1 = relatorioano1.get("despesas", {}).get(cat, 0)
        receita1 = relatorioano1.get("receitas", {}).get(cat, 0)
        despesa2 = relatorioano2.get("despesas", {}).get(cat, 0)
        receita2 = relatorioano2.get("receitas", {}).get(cat, 0)

        print("Despesas no ano 1: ", despesa1, "\n")
        print("Receitas no ano 1: ", receita1, "\n")
        print("Despesas no ano 2: ", despesa2, "\n")
        print("Receitas no ano 2: ", receita2, "\n")


        # Define valor1 e valor2 com base no sinal da diferença entre receita e despesa
        if despesa1 >= receita1 and despesa2 >= receita2:
            valor1 = -despesa1
            valor2 = -despesa2
            mesmo_tipo = 1
        elif despesa1 >= receita1 and despesa2 <= receita2: #Gains maximaux: on dépensait de fou et on on gagne de la thune maintenant
            valor1 = -despesa1
            valor2 = receita2
            mesmo_tipo = 0
        elif despesa1 <= receita1 and despesa2 <= receita2:
            valor1 = receita1
            valor2 = receita2
            mesmo_tipo = 1
        elif despesa1 <= receita1 and despesa2 >= receita2:
            valor1 = receita1
            valor2 = -despesa2
            mesmo_tipo = 0

        variacao = valor2 - valor1 #Diferenca > 0: tem menos

        dict_categoria = {
            "categoria": cat,
            "valorAno1": round(valor1, 2),
            "valorAno2": round(valor2, 2),
            "variacao": round(variacao, 2),
            "mesmo_tipo": mesmo_tipo
        }

        lista_dif_por_cat.append(dict_categoria)

        if variacao <= categoria_maior_gasto["variacao"]: #Despesas
            categoria_maior_gasto = dict_categoria
        elif variacao >= categoria_maior_ganho["variacao"]: #Receitas
            categoria_maior_ganho = dict_categoria

    return lista_dif_por_cat, [categoria_maior_gasto, categoria_maior_ganho]


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
                "variacao": {
                    "receitas": float,
                    "despesas": float,
                    "saldoFinal": float
                },
                "categorias_variacoes_extremas": [
                    {
                        "categoria": str,
                        "valorPeriodo1": float,
                        "valorPeriodo2": float,
                        "variacao": float
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

    print("\nRelatorio ano 1: ", relatorioano1, "\n")
    print("\nRelatorio ano 2: ", relatorioano2, "\n")

    diferenca_receitas = relatorioano2["receitas"]["total"] - relatorioano1["receitas"]["total"]
    diferenca_despesas = relatorioano2["despesas"]["total"] - relatorioano1["despesas"]["total"]
    diferenca_saldoFinal = relatorioano2["saldoFinal"] - relatorioano1["saldoFinal"]

    gastos_por_categoria, [cat_mais_gasto, cat_mais_ganho] = categoria_maior_dif_despesa(relatorioano1, relatorioano2)

    resumo = (
    f"Entre os anos de {ano1} e {ano2}, as receitas totais variaram em R$ {diferenca_receitas:.2f}, "
    f"e as despesas em R$ {diferenca_despesas:.2f}.\n"
    f"No fim de {ano1}, o saldo final era de R$ {relatorioano1['saldoFinal']}, "
    f"e passou a R$ {relatorioano2['saldoFinal']} no fim de {ano2}.\n"
    )

    if cat_mais_gasto["categoria"] is None:
        resumo += "Nenhuma variação significativa de gasto foi detectada.\n"
    if cat_mais_ganho["categoria"] is None:
        resumo += "Nenhuma variação significativa de ganho foi detectada.\n"
    else:
        resumo += f"\nAtenção aos gastos na categoria '{cat_mais_gasto['categoria']}':\n"
        if cat_mais_gasto["mesmo_tipo"] == 0:
            resumo += "O que era positivo no primeiro ano virou altamente negativo no segundo ano.\n"
        else:
            resumo += "O que já era negativo no primeiro ano continuou negativo no segundo.\n"

        resumo += (
            f"Totalizando gastos e beneficios em {ano1}: R$ {cat_mais_gasto['valorAno1']:.2f} na conta, contra "
            f"R$ {cat_mais_gasto['valorAno2']:.2f} em {ano2} "
            f"({cat_mais_gasto['variacao']:.2f} de variação).\n"
        )

        resumo += f"\nEntretanto houve uma melhoria na categoria '{cat_mais_ganho['categoria']}':\n"
        if cat_mais_ganho["mesmo_tipo"] == 0:
            resumo += "O que era negativo no primeiro ano virou muito positivo no segundo!\n"
        else:
            resumo += "O que já era positivo no primeiro ano se manteve positivo no segundo.\n"

        resumo += (
            f"Totalizando gastos e beneficios em {ano1}: R$ {cat_mais_ganho['valorAno1']:.2f} na conta, contra "
            f"R$ {cat_mais_ganho['valorAno2']:.2f} em {ano2} "
            f"({cat_mais_ganho['variacao']:.2f} de variação).\n"
        )

    resumo += "\nAumentos nas despesas:\n"
    aumentos = [item for item in gastos_por_categoria if item['variacao'] > 0]
    if aumentos:
        for item in aumentos:
            resumo += f" - {item['categoria']}: +R$ {item['variacao']:.2f}\n"
    else:
        resumo += "Nenhuma categoria teve aumento de despesas.\n"

    resumo += "\nReduções nas despesas:\n"
    reducoes = [item for item in gastos_por_categoria if item['variacao'] < 0]
    if reducoes:
        for item in reducoes:
            resumo += f" - {item['categoria']}: R$ {item['variacao']:.2f}\n"
    else:
        resumo += "Nenhuma categoria teve redução de despesas.\n"

    converter_PDF(resumo, "./tests/data/relatorios_pdf/comparativos.pdf")


    comparativo = {
        "ano1": { "receitas": relatorioano1["receitas"],  "despesas": relatorioano1["despesas"], "saldoFinal": relatorioano1["saldoFinal"]},
        "ano2": { "receitas": relatorioano2["receitas"],  "despesas": relatorioano2["despesas"], "saldoFinal": relatorioano2["saldoFinal"]},
        "diferencas": { "receitas": diferenca_receitas, "despesas": diferenca_despesas, "saldoFinal": diferenca_saldoFinal},
        "categorias_variacoes_extremas": [cat_mais_gasto, cat_mais_ganho],
        "resumo": resumo,
    }
        
    return { "Status": 200, "Content": comparativo}