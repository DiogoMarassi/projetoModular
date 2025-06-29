import pytest
from datetime import datetime
from modulos.lancamento import (
    criarLancamento, editarLancamento, removerLancamento,
    listarLancamentos, calcularSaldoMensal
)
from modulos.planejamento.planejamento import (
    calculaDivisaoGastos, editarDivisaoGastos, obterDivisaoSalva
)
from modulos.notificacao.notificacao import (
    salvarNotificacao, listarNotificacoes, resetarNotificacoes
)
from modulos.relatorio import gerar_relatorio_financeiro, gerar_comparativo


@pytest.fixture
def lancamento_teste():
    return {
        "descricao": "Teste Principal",
        "valor": 1000.0,
        "data": datetime(2025, 6, 15),
        "tipo": "receita",
        "categoria": "Salario"
    }

# === Testes de Lançamentos ===

def test_criar_editar_remover_lancamento(lancamento_teste):
    response = criarLancamento(lancamento_teste)
    assert "Success" in response
    lanc_id = response["Content"]["id"]

    novos_dados = lancamento_teste.copy()
    novos_dados["valor"] = 1200.0
    response_edit = editarLancamento(lanc_id, novos_dados)
    assert "Success" in response_edit

    response_remove = removerLancamento(lanc_id)
    assert "Success" in response_remove


def test_listar_lancamentos_com_filtros(lancamento_teste):
    criarLancamento(lancamento_teste)
    filtros = {
        "valor": lancamento_teste["valor"],
        "tipo": lancamento_teste["tipo"],
        "categoria": lancamento_teste["categoria"]
    }
    response = listarLancamentos(filtros)
    assert "Success" in response
    assert isinstance(response["Content"], list)


def test_calcular_saldo_mensal_com_lancamento(lancamento_teste):
    criarLancamento(lancamento_teste)
    response = calcularSaldoMensal(6, 2025)
    assert "Success" in response
    assert response["Content"]["mes"] == 6
    assert isinstance(response["Content"]["saldo"], float)

# === Testes de Planejamento ===

def test_calcula_e_edita_divisao_gastos():
    resposta = calculaDivisaoGastos(3000.0)
    assert "Success" in resposta
    assert resposta["Content"]["salario"] == 3000.0

    nova_divisao = {
        "salario": 3000.0,
        "divisao": {
            "moradia": 900.0,
            "alimentacao": 600.0,
            "transporte": 300.0,
            "lazer": 300.0,
            "saude": 300.0,
            "educacao": 300.0,
            "guardar": 300.0
        }
    }
    editado = editarDivisaoGastos(nova_divisao)
    assert "Success" in editado

    obtido = obterDivisaoSalva()
    assert "Success" in obtido
    assert obtido["Content"]["salario"] == 3000.0

# === Testes de Notificações ===

def test_salvar_e_listar_notificacoes():
    resetarNotificacoes()
    salvar = salvarNotificacao("Notificação de teste")
    assert salvar["Status"] == 200

    lista = listarNotificacoes()
    assert lista["Status"] == 200
    assert any("teste" in n["conteudo"].lower() for n in lista["Content"])

# === Testes de Relatórios ===

def test_gerar_relatorio_e_comparativo(lancamento_teste):
    # Criar lançamento em 2024
    criarLancamento({
        **lancamento_teste,
        "data": datetime(2024, 6, 15),
        "descricao": "Salário 2024"
    })

    # Criar lançamento em 2025
    criarLancamento(lancamento_teste)

    periodo = {
        "data_inicio": datetime(2025, 6, 1),
        "data_final": datetime(2025, 6, 30)
    }
    relatorio = gerar_relatorio_financeiro(periodo, PDF=False)
    assert relatorio["Status"] == 200
    assert "saldoInicial" in relatorio["Content"]

    comparativo = gerar_comparativo(2024, 2025)
    assert comparativo["Status"] == 200
    assert "diferencas" in comparativo["Content"]
