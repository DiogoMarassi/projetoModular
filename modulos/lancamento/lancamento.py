"""
Módulo Lançamentos Financeiros
INF1301 - Programação Modular
Responsável: Pedro Nogueira

Este módulo permite ao usuário:
- Cadastrar, editar, listar e remover lançamentos financeiros,
    organizando seu fluxo de caixa. Os lançamentos podem ser de receita ou despesa.
- Cálculo do saldo mensal
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import atexit
from config import categorias, tipos


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_arquivo_dados = os.path.join(BASE_DIR, "data", "lancamentos.json")

# Dados encapsulados - lista de lançamentos em memória

_lancamentos: List[Dict[str, object]] = []
_proximo_id: int = 1

def _carregar_dados():
    """Carrega os dados do arquivo JSON para a memória"""
    global _lancamentos, _proximo_id
    
    if os.path.exists(_arquivo_dados):
        try:
            with open(_arquivo_dados, 'r', encoding='utf-8') as arquivo:
                dados = json.load(arquivo)
                _lancamentos = dados.get('lancamentos', [])
                _proximo_id = dados.get('proximo_id', 1)
                
                # Converte strings de data de volta para datetime
                for lancamento in _lancamentos:
                    if isinstance(lancamento['data'], str):
                        lancamento['data'] = datetime.fromisoformat(lancamento['data'])
        except (json.JSONDecodeError, KeyError, ValueError):
            # Se houver erro no arquivo, reinicia com dados vazios
            _lancamentos = []
            _proximo_id = 1


def _salvar_dados():
    """Salva os dados da memória para o arquivo JSON"""
    dados_para_salvar = {
        'lancamentos': [],
        'proximo_id': _proximo_id
    }
    
    # Converte datetime para string para serialização JSON
    for lancamento in _lancamentos:
        lancamento_copy = lancamento.copy()
        if isinstance(lancamento_copy['data'], datetime):
            lancamento_copy['data'] = lancamento_copy['data'].isoformat()
        dados_para_salvar['lancamentos'].append(lancamento_copy)
    
    try:
        with open(_arquivo_dados, 'w', encoding='utf-8') as arquivo:
            json.dump(dados_para_salvar, arquivo, indent=2, ensure_ascii=False)
    except IOError:
        # Em caso de erro ao salvar, continua com dados em memória
        pass

def setArquivoPersistencia(caminho: str) -> None:
    """
    Altera o caminho do arquivo de persistência (para testes).
    """
    global _arquivo_dados
    _arquivo_dados = caminho
    _carregar_dados()

def resetarDados() -> None:
    """
    Limpa todas as notificações em memória (para testes).
    """
    global _lancamentos
    _lancamentos = []

def _validar_dados_lancamento(dados):
    """Valida os dados de um lançamento"""
    if not isinstance(dados, dict):
        return False
    
    # Verifica campos obrigatórios
    campos_obrigatorios = ['descricao', 'valor', 'data', 'tipo', 'categoria']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return False
    
    # Valida descrição
    if not isinstance(dados['descricao'], str) or dados['descricao'].strip() == '':
        return False
    
    # Valida valor
    if not isinstance(dados['valor'], (int, float)) or dados['valor'] <= 0:
        return False
    
    # Valida data
    if not isinstance(dados['data'], datetime):
        return False
    
    # Valida tipo
    if dados['tipo'] not in tipos:
        return False
    
    # Valida categoria
    if dados['categoria'] not in categorias:
        return False
    
    return True


def _validar_data(mes, ano):
    """Valida se mês e ano são válidos"""
    if not isinstance(mes, int) or not isinstance(ano, int):
        return False
    
    if mes < 1 or mes > 12:
        return False
    
    if ano < 1900 or ano > 2100:
        return False
    
    return True


def _encontrar_lancamento_por_id(id_lancamento):
    """Encontra um lançamento pelo ID"""
    for lancamento in _lancamentos:
        if lancamento['id'] == id_lancamento:
            return lancamento
    return None

# Persistência entre execuções

# Inicializa os dados ao importar o módulo
_carregar_dados()

# Salva os dados ao final da execução
atexit.register(_salvar_dados)

def criarLancamento(dados):
    """
    Cria um novo lançamento financeiro
    
    Parâmetros:
        dados: Dicionário com descricao (string), valor (float), data (datetime), 
               tipo (string), categoria (string)
    
    Retorna:
        Em caso de sucesso: {"Status": 201, "Content": {"id": int, "dados": dict}}
        Em caso de erro: {"Status": 400, "Content": "Dados inválidos ou incompletos."}
    """
    global _proximo_id
        
    if not _validar_dados_lancamento(dados):
        return {"Status": 400, "Content": "Dados inválidos ou incompletos."}
    
    # Cria o novo lançamento
    novo_lancamento = {
        'id': _proximo_id,
        'descricao': dados['descricao'].strip(),
        'valor': float(dados['valor']),
        'data': dados['data'],
        'tipo': dados['tipo'],
        'categoria': dados['categoria']
    }
    
    _lancamentos.append(novo_lancamento)
    _proximo_id += 1
    
    return {
        "Status": 201,
        "Content": {
            "id": novo_lancamento['id'],
            "descricao": novo_lancamento['descricao'],
            "valor": novo_lancamento['valor'],
            "data": novo_lancamento['data'],
            "tipo": novo_lancamento['tipo'],
            "categoria": novo_lancamento['categoria']
        }
    }


def editarLancamento(id_lancamento, novos_dados):
    """
    Edita um lançamento financeiro existente
    
    Parâmetros:
        id_lancamento: ID do lançamento a ser editado
        novos_dados: Novos dados do lançamento
    
    Retorna:
        Em caso de sucesso: {"Status": 200, "Content": "Lançamento atualizado com sucesso."}
        Em caso de dados inválidos: {"Status": 400, "Content": "Dados inválidos."}
        Em caso de lançamento não encontrado: {"Status": 404, "Content": "Lançamento não encontrado."}
    """
    if not isinstance(id_lancamento, int):
        return {"Status": 400, "Content": "Dados inválidos."}
    
    lancamento = _encontrar_lancamento_por_id(id_lancamento)
    if not lancamento:
        return {"Status": 404, "Content": "Lançamento não encontrado."}
    
    if not _validar_dados_lancamento(novos_dados):
        return {"Status": 400, "Content": "Dados inválidos."}
    
    # Atualiza os dados do lançamento
    lancamento['descricao'] = novos_dados['descricao'].strip()
    lancamento['valor'] = float(novos_dados['valor'])
    lancamento['data'] = novos_dados['data']
    lancamento['tipo'] = novos_dados['tipo']
    lancamento['categoria'] = novos_dados['categoria']
    
    return {"Status": 200, "Content": "Lançamento atualizado com sucesso."}


def removerLancamento(id_lancamento):
    """
    Remove um lançamento financeiro
    
    Parâmetros:
        id_lancamento: ID do lançamento a ser removido
    
    Retorna:
        Em caso de sucesso: {"Status": 200, "Content": "Lançamento removido com sucesso."}
        Em caso de lançamento não encontrado: {"Status": 404, "Content": "Lançamento não encontrado."}
    """
    if not isinstance(id_lancamento, int):
        return {"Status": 404, "Content": "Lançamento não encontrado."}
    
    lancamento = _encontrar_lancamento_por_id(id_lancamento)
    if not lancamento:
        return {"Status": 404, "Content": "Lançamento não encontrado."}
    
    _lancamentos.remove(lancamento)
    
    return {"Status": 200, "Content": "Lançamento removido com sucesso."}


from config import filtros_validos
def listarLancamentos(filtros=None):
    if filtros is None:
        filtros = {}
    for chave in filtros:
        if chave not in filtros_validos:
            return {"Status": 400, "Content": f"Filtro inválido: {chave}"}

    lancamentos_filtrados = []

    for lancamento in _lancamentos:
        incluir = True

        if 'valor' in filtros and filtros['valor'] is not None:
            if not isinstance(filtros['valor'], (int, float)):
                continue
            if lancamento['valor'] != filtros['valor']:
                incluir = False

        if 'data' in filtros and filtros['data'] is not None:
            if not isinstance(filtros['data'], datetime):
                continue
            if lancamento['data'].date() != filtros['data'].date():
                incluir = False

        if 'tipo' in filtros and filtros['tipo'] is not None:
            if not isinstance(filtros['tipo'], str):
                continue
            if lancamento['tipo'] != filtros['tipo']:
                incluir = False

        if 'categoria' in filtros and filtros['categoria'] is not None:
            if not isinstance(filtros['categoria'], str):
                continue
            if lancamento['categoria'] != filtros['categoria']:
                incluir = False

        if incluir:
            lancamentos_filtrados.append(lancamento.copy())

    if not lancamentos_filtrados:
        return {"Status": 404, "Content": "Nenhum lançamento encontrado."}

    lancamentos_filtrados.sort(key=lambda x: x['data'], reverse=True)

    return {"Status": 200, "Content": lancamentos_filtrados}



def calcularSaldoMensal(mes, ano):
    """
    Calcula o saldo mensal com base nos lançamentos do mês/ano especificado
    
    Parâmetros:
        mes: Mês (1-12)
        ano: Ano
    
    Retorna:
        Em caso de sucesso: {"Status": 200, "Content": {"saldo": float, "mes": int, "ano": int}}
        Em caso de data inválida: {"Status": 400, "Content": "Data inválida"}
    """
    if not _validar_data(mes, ano):
        return {"Status": 400, "Content": "Data inválida"}
    
    saldo = 0.0
    
    for lancamento in _lancamentos:
        if lancamento['data'].month == mes and lancamento['data'].year == ano:
            if lancamento['tipo'] == 'receita':
                saldo += lancamento['valor']
            elif lancamento['tipo'] == 'despesa':
                saldo -= lancamento['valor']
    
    return {
        "Status": 200,
        "Content": {
            "saldo": round(saldo, 2),
            "mes": mes,
            "ano": ano
        }
    }


def somarDespesasPorCategoria(categoria: str) -> float:
    """
    Retorna a soma de todas as despesas da categoria informada.
    """
    return sum(
        lanc["valor"]
        for lanc in _lancamentos
        if lanc["categoria"] == categoria and lanc["tipo"] == "despesa"
    )