"""
Arquivo de teste para demonstrar o uso do módulo Lançamentos Financeiros
"""

import os
from datetime import datetime
import shutil
import pytest
from modulos.lancamento import *

# Caminho do arquivo de dados usado pelo módulo
ARQUIVO_DADOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/lancamentos.json"))
ARQUIVO_BACKUP = ARQUIVO_DADOS + ".bak"

@pytest.fixture(autouse=True, scope="module")
def backup_e_limpeza_arquivo():
    arquivo_existia_antes = os.path.exists(ARQUIVO_DADOS)
    if arquivo_existia_antes:
        shutil.copy2(ARQUIVO_DADOS, ARQUIVO_BACKUP)

    yield  # Aqui rodam os testes

    # Depois dos testes: restaura o backup ou remove o arquivo criado
    if arquivo_existia_antes and os.path.exists(ARQUIVO_BACKUP):
        shutil.move(ARQUIVO_BACKUP, ARQUIVO_DADOS)
    elif not arquivo_existia_antes and os.path.exists(ARQUIVO_DADOS):
        os.remove(ARQUIVO_DADOS)

def test_criar_lancamento_sucesso():
    """Testa criação de lançamento com dados válidos (espera 201)"""
    dados = {
        "descricao": "Salário",
        "valor": 3000.00,
        "data": datetime(2025, 5, 1),
        "tipo": "receita",
        "categoria": "Salario"
    }
    response = criarLancamento(dados)
    assert response["Success"] == 201
    assert "id" in response["Content"]
    assert response["Content"]["descricao"] == dados["descricao"]
    print("✓ Teste criar lançamento com sucesso passou")

def test_criar_lancamento_dados_invalidos():
    """Testa criação com campos faltando (espera 400)"""
    dados = {
        "descricao": "",
        "valor": -100,
        "data": "invalid_data",
        "tipo": "unknown_type",
        "categoria": "Invalid"
    }
    response = criarLancamento(dados)
    assert response["Error"] == 400
    assert response["Content"] == "Dados inválidos ou incompletos."
    print("✓ Teste criar lançamento com dados inválidos passou")

def test_editar_lancamento_sucesso():
    """Testa edição de lançamento sucedida (espera 200)"""
    # Primeiro cria um lançamento
    dados = {
        "descricao": "Salário Original",
        "valor": 3200.00,
        "data": datetime(2025, 6, 1),
        "tipo": "receita",
        "categoria": "Salario"
    }
    response = criarLancamento(dados)
    lancamento_id = response["Content"]["id"]
    
    # Depois edita
    dadosalt = {
        "descricao": "Salário Atualizado",
        "valor": 3300.00,
        "data": datetime(2025, 7, 1),
        "tipo": "receita",
        "categoria": "Salario"
    }
    responsealt = editarLancamento(lancamento_id, dadosalt)
    assert responsealt["Success"] == 200
    assert responsealt["Content"] == "Lançamento atualizado com sucesso."
    print("✓ Teste editar lançamento com sucesso passou")

def test_editar_lancamento_nao_encontrado():
    """Testa edição de lançamento inexistente (espera 404)"""
    dados = {
        "descricao": "Salário Atualizado",
        "valor": 3200.00,
        "data": datetime(2025, 6, 1),
        "tipo": "receita",
        "categoria": "Salario"
    }
    response = editarLancamento(999, dados)  # ID inexistente
    assert response["Error"] == 404
    assert response["Content"] == "Lançamento não encontrado."
    print("✓ Teste editar lançamento não encontrado passou")

def test_remover_lancamento_sucesso():
    """Testa remoção de lançamento existente (espera 200)"""
    # Primeiro cria um lançamento
    dados = {
        "descricao": "Lançamento para remover",
        "valor": 100.00,
        "data": datetime(2025, 6, 1),
        "tipo": "despesa",
        "categoria": "Outros"
    }
    response = criarLancamento(dados)
    lancamento_id = response["Content"]["id"]
    
    # Depois remove
    responserem = removerLancamento(lancamento_id)
    assert responserem["Success"] == 200
    assert responserem["Content"] == "Lançamento removido com sucesso."
    print("✓ Teste remover lançamento com sucesso passou")

def test_remover_lancamento_nao_encontrado():
    """Testa remoção de lançamento inexistente (espera 404)"""
    response = removerLancamento(999)  # ID inexistente
    assert response["Error"] == 404
    assert response["Content"] == "Lançamento não encontrado."
    print("✓ Teste remover lançamento não encontrado passou")

def test_listar_lancamentos_com_filtros():
    """Testa lista de lançamentos com filtros (espera 200)"""
    # Primeiro cria alguns lançamentos para ter dados
    dados1 = {
        "descricao": "Compra supermercado",
        "valor": 150.00,
        "data": datetime(2025, 5, 15),
        "tipo": "despesa",
        "categoria": "Alimentação"
    }
    criarLancamento(dados1)
    
    filtros = {"tipo": "despesa", "categoria": "Alimentação"}
    response = listarLancamentos(filtros)
    assert response["Success"] == 200
    assert isinstance(response["Content"], list)
    print("✓ Teste listar lançamentos com filtros passou")

def test_listar_lancamentos_sem_resultados():
    """Testa lista de lançamentos vazia (espera 404)"""
    filtros = {"valor": 999999.0}  # Valor que não existe
    response = listarLancamentos(filtros)
    assert response["Error"] == 404
    assert response["Content"] == "Nenhum lançamento encontrado."
    print("✓ Teste listar lançamentos sem resultados passou")

def test_calcular_saldo_mensal_sucesso():
    """Testa cálculo de saldo mensal sucedido (espera 200)"""
    # Cria alguns lançamentos para maio de 2025
    dados_receita = {
        "descricao": "Salário maio",
        "valor": 2000.00,
        "data": datetime(2025, 5, 1),
        "tipo": "receita",
        "categoria": "Salario"
    }
    dados_despesa = {
        "descricao": "Conta de luz",
        "valor": 200.00,
        "data": datetime(2025, 5, 10),
        "tipo": "despesa",
        "categoria": "Moradia"
    }
    criarLancamento(dados_receita)
    criarLancamento(dados_despesa)
    
    response = calcularSaldoMensal(5, 2025)
    assert response["Success"] == 200
    assert response["Content"]["mes"] == 5
    assert response["Content"]["ano"] == 2025
    assert "saldo" in response["Content"]
    print("✓ Teste calcular saldo mensal com sucesso passou")

def test_calcular_saldo_mensal_data_invalida():
    """Testa cálculo de saldo mensal com data inválida (espera 400)"""
    response = calcularSaldoMensal(13, 2025)  # Mês inválido
    assert response["Error"] == 400
    assert response["Content"] == "Data inválida"
    print("✓ Teste calcular saldo mensal com data inválida passou")

def exemplo_uso_basico():
    """Exemplo básico de uso do módulo"""
    print("\n=== EXEMPLO DE USO DO MÓDULO ===")
    
    # Criar um lançamento de receita
    receita = {
        "descricao": "Salário de junho",
        "valor": 3500.00,
        "data": datetime(2025, 6, 1),
        "tipo": "receita",
        "categoria": "Salario"
    }
    
    resultado = criarLancamento(receita)
    print(f"Lançamento criado: {resultado}")
    
    # Criar um lançamento de despesa
    despesa = {
        "descricao": "Supermercado",
        "valor": 450.00,
        "data": datetime(2025, 6, 5),
        "tipo": "despesa",
        "categoria": "Alimentação"
    }
    
    resultado = criarLancamento(despesa)
    print(f"Despesa criada: {resultado}")
    
    # Listar todos os lançamentos
    lista = listarLancamentos()
    print(f"Lançamentos listados: {len(lista['Content'])} itens")
    
    # Calcular saldo do mês
    saldo = calcularSaldoMensal(6, 2025)
    print(f"Saldo mensal: {saldo}")

if __name__ == "__main__":
    # Executa os testes
    print("Executando testes do módulo Lançamentos Financeiros...\n")
    
    try:
        test_criar_lancamento_sucesso()
        test_criar_lancamento_dados_invalidos()
        test_editar_lancamento_sucesso()
        test_editar_lancamento_nao_encontrado()
        test_remover_lancamento_sucesso()
        test_remover_lancamento_nao_encontrado()
        test_listar_lancamentos_com_filtros()
        test_listar_lancamentos_sem_resultados()
        test_calcular_saldo_mensal_sucesso()
        test_calcular_saldo_mensal_data_invalida()
        
        print("\n✅ Todos os testes passaram com sucesso!")
        
        # Exemplo de uso
        exemplo_uso_basico()
        
    except AssertionError as e:
        print(f"\n❌ Teste falhou: {e}")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")