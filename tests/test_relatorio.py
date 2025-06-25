from modulos.relatorio import gerar_relatorio_financeiro, gerar_comparativo
from datetime import datetime

# --- Casos de testes automatizados para a geração do relatório ---
def test_gerar_relatorio_financeiro_sucesso():
    periodo = {"data_inicio": datetime(2020, 5, 1),
               "data_final": datetime(2023, 5, 31)
                }
    response = gerar_relatorio_financeiro(periodo)
    assert response["Status"] == 200
    assert "saldoInicial" in response["Content"]
    assert "saldoFinal" in response["Content"]


def test_gerar_relatorio_financeiro_sem_lancamentos():
    periodo = {"data_inicio": datetime(2025, 1, 1),
               "data_final": datetime(2026, 1, 31)
               }
    response = gerar_relatorio_financeiro(periodo)
    assert response["Status"] == 404
    assert response["Content"] == "Nenhum lançamento encontrado"



def test_gerar_relatorio_financeiro_periodo_invalido():
    periodo = {"data_inicio": datetime(2027, 5, 31),
               "data_final": datetime(2025, 5, 31)
               }
    response = gerar_relatorio_financeiro(periodo)
    assert response["Status"] == 400
    assert response["Content"] == "Período inválido."


# --- Casos de testes automatizados para a geraçao do comparativo ---

def test_gerar_comparativo_sucesso():
    response = gerar_comparativo(2020, 2021)
    assert response["Status"] == 200
    assert "diferencas" in response["Content"]
    assert "categorias_variacoes_extremas" in response["Content"]


def test_gerar_comparativo_ano_invalido():
    response = gerar_comparativo(-2024, 2025)
    assert response["Status"] == 400
    assert response["Content"] == "Ano inválido"