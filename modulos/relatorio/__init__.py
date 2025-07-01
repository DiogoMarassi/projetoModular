### __init__.py define o diretório 'relatorio' como um módulo importável ###
from .relatorio import (
    gerar_relatorio_financeiro,
    gerar_comparativo,
    gerar_grafico_pizza_despesas,
)

__all__ = [
    'gerar_relatorio_financeiro',
    'gerar_comparativo',
    'gerar_grafico_pizza_despesas',
]