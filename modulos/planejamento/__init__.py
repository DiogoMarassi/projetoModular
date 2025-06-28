### __init__.py define o diretório 'relatorio' como um módulo ###
from .planejamento import (
    calculaDivisaoGastos,
    editarDivisaoGastos,
    obterDivisaoSalva,
    calculaDivisaoDoUltimoSalario
)

# __all__ define as funções que podem ser importadas ###
__all__ = [
    'calculaDivisaoGastos',
    'editarDivisaoGastos',
    'obterDivisaoSalva',
    'calculaDivisaoDoUltimoSalario'
]