import pytest
from datetime import datetime
import os
from datetime import datetime

from modulos.lancamento import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARQUIVO_TESTE = os.path.join(BASE_DIR, "tests", "data", "lancamentos.json")

# Fixture para preparar ambiente limpo
@pytest.fixture(autouse=True)
def ambiente_limpo():
    setArquivoPersistencia(ARQUIVO_TESTE)
    resetarDados()
    if os.path.exists(ARQUIVO_TESTE):
        os.remove(ARQUIVO_TESTE)
    yield
    if os.path.exists(ARQUIVO_TESTE):
        os.remove(ARQUIVO_TESTE)
        
# ---------- FIXTURE: Lançamento válido ----------
@pytest.fixture
def dados_validos():
    return {
        "descricao": "Teste",
        "valor": 100.0,
        "data": datetime(2025, 6, 1),
        "tipo": "receita",
        "categoria": "Salario"
    }

# ---------- TESTES: criação ----------
@pytest.mark.parametrize("dados", [
    # descrição inválida
    {"descricao": "", "valor": 100, "data": datetime(2025, 6, 1), "tipo": "receita", "categoria": "Salario"},
    {"descricao": 123, "valor": 100, "data": datetime(2025, 6, 1), "tipo": "receita", "categoria": "Salario"},
    # valor inválido
    {"descricao": "X", "valor": -10, "data": datetime(2025, 6, 1), "tipo": "receita", "categoria": "Salario"},
    {"descricao": "X", "valor": "cem", "data": datetime(2025, 6, 1), "tipo": "receita", "categoria": "Salario"},
    # data inválida
    {"descricao": "X", "valor": 100, "data": "2025-01-01", "tipo": "receita", "categoria": "Salario"},
    {"descricao": "X", "valor": 100, "data": None, "tipo": "receita", "categoria": "Salario"},
    # tipo inválido
    {"descricao": "X", "valor": 100, "data": datetime(2025, 6, 1), "tipo": "entrada", "categoria": "Salario"},
    # categoria inválida
    {"descricao": "X", "valor": 100, "data": datetime(2025, 6, 1), "tipo": "receita", "categoria": "OutroX"},
])
def test_criar_lancamento_dados_invalidos(dados):
    response = criarLancamento(dados)
    assert response["Status"] == 400

def test_criar_lancamento_valido(dados_validos):
    response = criarLancamento(dados_validos)
    assert response["Status"] == 201
    assert response["Content"]["descricao"] == dados_validos["descricao"]

# ---------- TESTES: edição ----------
def test_editar_lancamento_valido(dados_validos):
    criado = criarLancamento(dados_validos)
    id_lanc = criado["Content"]["id"]
    novos_dados = dados_validos.copy()
    novos_dados["descricao"] = "Atualizado"
    response = editarLancamento(id_lanc, novos_dados)
    assert response["Status"] == 200

def test_editar_lancamento_nao_existente(dados_validos):
    response = editarLancamento(99999, dados_validos)
    assert response["Status"] == 404

def test_editar_lancamento_com_id_invalido(dados_validos):
    assert editarLancamento("abc", dados_validos)["Status"] == 400
    assert editarLancamento(None, dados_validos)["Status"] == 400

@pytest.mark.parametrize("dados", [
    {"descricao": "", "valor": 100, "data": datetime(2025, 6, 1), "tipo": "receita", "categoria": "Salario"},
])
def test_editar_lancamento_com_dados_invalidos(dados, dados_validos):
    criado = criarLancamento(dados_validos)
    id_lanc = criado["Content"]["id"]
    assert editarLancamento(id_lanc, dados)["Status"] == 400

# ---------- TESTES: remoção ----------
def test_remover_lancamento_valido(dados_validos):
    criado = criarLancamento(dados_validos)
    id_lanc = criado["Content"]["id"]
    response = removerLancamento(id_lanc)
    assert response["Status"] == 200

def test_remover_lancamento_nao_existente():
    assert removerLancamento(99999)["Status"] == 404

def test_remover_lancamento_com_id_invalido():
    assert removerLancamento("abc")["Status"] == 404
    assert removerLancamento(None)["Status"] == 404

# ---------- TESTES: listar ----------
@pytest.fixture
def lancamento_listavel():
    dados = {
        "descricao": "Supermercado",
        "valor": 200.0,
        "data": datetime(2025, 6, 10),
        "tipo": "despesa",
        "categoria": "Alimentação"
    }
    criarLancamento(dados)
    return dados

@pytest.mark.parametrize("filtros", [
    {"foo": "bar"},
    {"valor": 100, "extra": 1},
    {"tipo": "despesa", "errado": "ok"},
])
def test_listar_lancamentos_com_chave_invalida(filtros):
    response = listarLancamentos(filtros)
    assert response["Status"] == 400
    assert "Filtro inválido" in response["Content"]

@pytest.mark.parametrize("filtros", [
    {"valor": "cem"},
    {"data": "hoje"},
    {"tipo": 123},
    {"categoria": 999}
])
def test_listar_lancamentos_com_tipo_invalido(filtros):
    response = listarLancamentos(filtros)
    assert response["Status"] == 404

@pytest.mark.parametrize("filtros", [
    {"valor": 999999.0},
    {"data": datetime(2030, 1, 1)},
    {"tipo": "receita"},
    {"categoria": "Moradia"}
])
def test_listar_lancamentos_com_filtro_valido(lancamento_listavel, filtros):
    filtros = {"tipo": "despesa", "categoria": "Alimentação"}
    response = listarLancamentos(filtros)
    assert response["Status"] == 200
    assert isinstance(response["Content"], list)
    assert any(l["descricao"] == "Supermercado" for l in response["Content"])

# ---------- TESTES: saldo mensal ----------
def test_calcular_saldo_mensal_valido():
    response = calcularSaldoMensal(6, 2025)
    assert response["Status"] == 200
    assert "saldo" in response["Content"]

@pytest.mark.parametrize("mes,ano", [
    (0, 2025), (13, 2025), (5, 1899), (5, 2101), ("junho", 2025), (5, "ano"), (None, 2025)
])
def test_calcular_saldo_mensal_data_invalida(mes, ano):
    response = calcularSaldoMensal(mes, ano)
    assert response["Status"] == 400

@pytest.mark.parametrize("mes,ano", [(1, 2030), (2, 2040), (12, 2099)])
def test_calcular_saldo_sem_lancamentos(mes, ano):
    response = calcularSaldoMensal(mes, ano)
    assert response["Status"] == 200
    assert response["Content"]["saldo"] == 0.0
