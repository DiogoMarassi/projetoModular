import json
import os
from datetime import datetime
from numpy import random

# Categorias e tipos possíveis
from config import categorias, tipos

# Passeio nos arquivos (até encontrar a pasta de testes)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_TESTE = os.path.join(BASE_DIR, "lancamentos_testes.json")

def gerar_lancamentos(quantidade=50, anos=(2020, 2024)):
    lancamentos = []

    for i in range(quantidade):
        ano = random.randint(anos[0], anos[1])
        mes = random.randint(1, 12)
        dia = random.randint(1, 28)
        tipo = random.choice(tipos)
        valor = round(random.uniform(1000, 5000), 2) if tipo == 'receita' else round(random.uniform(10, 500), 2)
        categoria = random.choice(categorias)
        descricao = f"Lançamento {i}"

        lancamento = {
            "descricao": descricao,
            "valor": valor,
            "data": datetime(ano, mes, dia).isoformat(),  # transforma para string ISO
            "tipo": tipo,
            "categoria": categoria
        }

        lancamentos.append(lancamento)

    return lancamentos

def salvar_lancamentos_em_json(lancamentos, caminho=ARQUIVO_TESTE):
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(lancamentos, f, ensure_ascii=False, indent=4)
    print(f"{len(lancamentos)} lançamentos salvos em {caminho}")

# Se rodar direto o script, gera e salva
if __name__ == "__main__":
    dados = gerar_lancamentos()
    salvar_lancamentos_em_json(dados)