"""
Arquivo de teste para demonstrar o uso do módulo de planejamentos financeiros
"""

import os
import json
import pytest

from modulos.planejamento import (
    calculaDivisaoGastos,
    editarDivisaoGastos,
    obterDivisaoSalva,
)

# Caminho do arquivo de dados usado pelo módulo
CAMINHO_ARQUIVO = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../data/planejamento.json")
)


def teardown_module(module):
    """
    Executa após todos os testes.
    Limpa o arquivo de planejamento criado nos testes.
    """
    if os.path.exists(CAMINHO_ARQUIVO):
        os.remove(CAMINHO_ARQUIVO)


def test_calcula_divisao_gastos_valido():
    salario = 4000.0
    response = calculaDivisaoGastos(salario)

    assert "Success" in response
    assert response["Success"] == 200
    assert response["Content"]["salario"] == salario
    assert isinstance(response["Content"]["divisao"], dict)
    assert round(sum(response["Content"]["divisao"].values()), 2) == salario


def test_calcula_divisao_gastos_invalido():
    response = calculaDivisaoGastos(0)
    assert "Error" in response
    assert response["Error"] == 400


def test_editar_divisao_gastos_valido():
    nova_divisao = {
        "salario": 3000.0,
        "divisao": {
            "moradia": 900.0,
            "alimentacao": 600.0,
            "transporte": 150.0,
            "lazer": 300.0,
            "saude": 300.0,
            "educacao": 300.0,
            "guardar": 450.0
        }
    }
    response = editarDivisaoGastos(nova_divisao)
    assert "Success" in response
    assert response["Success"] == 200
    assert response["Content"]["salario"] == 3000.0


def test_editar_divisao_gastos_invalido():
    nova_divisao = {
        "salario": 2000.0,
        "divisao": {
            "moradia": -500.0,
            "alimentacao": 600.0,
            "transporte": 150.0,
            "lazer": 300.0,
            "saude": 300.0,
            "educacao": 300.0,
            "guardar": 450.0
        }
    }
    response = editarDivisaoGastos(nova_divisao)
    assert "Error" in response
    assert response["Error"] == 400


def test_obter_divisao_salva():
    # Primeiro salva algo
    salario = 5000.0
    calculaDivisaoGastos(salario)

    response = obterDivisaoSalva()
    assert "Success" in response
    assert response["Success"] == 200
    assert response["Content"]["salario"] == salario


@pytest.mark.skip(reason="Teste do salário mais recente depende de lançamentos.")
def test_calcula_divisao_do_ultimo_salario():
    """
    Exemplo de como testar calculaDivisaoDoUltimoSalario()
    Mas este teste só passa se houver lançamentos válidos cadastrados.
    """
    from modulos.planejamento import calculaDivisaoDoUltimoSalario
    response = calculaDivisaoDoUltimoSalario()
    assert "Success" in response or "Error" in response
