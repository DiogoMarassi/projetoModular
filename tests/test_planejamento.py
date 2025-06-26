import pytest
from modulos.planejamento import calculaDivisaoGastos, editarDivisaoGastos, obterDivisaoSalva

def test_calculo_valido():
    salario = 3000.00
    response = calculaDivisaoGastos(salario)
    assert response["Success"] == 200
    assert response["Content"]["salario"] == salario
    assert response["Content"]["divisao"]["moradia"] == pytest.approx(900.00, rel=1e-2)

def test_calculo_invalido():
    response = calculaDivisaoGastos(0)
    assert response["Error"] == 400
    assert response["Content"] == "Salário Inválido"

def test_edicao_valida():
    nova_divisao = {
        "salario": 3000.00,
        "divisao": {
            "moradia": 900.00,
            "alimentacao": 600.00,
            "transporte": 450.00,
            "lazer": 300.00,
            "saude": 300.00,
            "educacao": 150.00,
            "poupanca": 300.00
        }
    }
    response = editarDivisaoGastos(nova_divisao)
    assert response["Success"] == 200
    assert response["Content"] == nova_divisao

def test_edicao_invalida():
    nova_divisao = {
        "salario": 3000.00,
        "divisao": {
            "moradia": -900.00,
            "alimentacao": 600.00,
            "transporte": 450.00,
            "lazer": 300.00,
            "saude": 300.00,
            "educacao": 150.00,
            "poupanca": 300.00
        }
    }
    response = editarDivisaoGastos(nova_divisao)
    assert response["Error"] == 400
    assert response["Content"] == "Nova divisão de gastos inválida"
