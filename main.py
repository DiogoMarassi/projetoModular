"""
Módulo Principal
INF1301 – Programação Modular
Responsáveis: Todos

Este módulo chama os outros quatro módulos e apresenta um menu
para que o usuário possa realizar as ações desejadas.
"""

from modulos.lancamento import *
from modulos.relatorio import *
from modulos.notificacao.notificacao import *
from modulos.planejamento.planejamento import *

from pprint import pprint #Para um pretty print no console
from datetime import datetime
import os
from dotenv import load_dotenv

from config import categorias

# Variáveis para as notificões
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
chat_id = 1665469613


## MENU NOTIFICACOES
def menu_notificacoes(chat_id: int):
    while True:
        print("\n===== Menu Notificações =====")
        print("1. Listar todas as notificações")
        print("2. Filtrar notificações por data")
        print("3. Enviar notificação para Telegram")
        print("4. Resetar notificações (APAGAR TUDO)")
        print("5. Sair")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            response = listarNotificacoes()
            if response["Status"] == 200:
                print("\n📋 Notificações:")
                for n in response["Content"]:
                    print(f"- {n['data']} : {n['conteudo']}")
            else:
                print(response["Content"])

        elif opcao == "2":
            data_inicio = input("Digite a data de início (DD/MM/AAAA): ")
            data_fim = input("Digite a data de fim (DD/MM/AAAA): ")
            response = filtrarNotificacoesPorPeriodo(data_inicio, data_fim)
            if response["Status"] == 200:
                print("\n📅 Notificações no período:")
                for n in response["Content"]:
                    print(f"- {n['data']} : {n['conteudo']}")
            else:
                print(response["Content"])

        elif opcao == "3":
            conteudo = input("Digite o conteúdo da notificação: ")
            response = enviarNotificacao(chat_id, conteudo)
            if response["Status"] == 200:
                print("\nMensagem enviada para o Telegram e salva localmente.")
            else:
                print(f"\nErro: {response['Content']}")

        elif opcao == "4":
            confirm = input("Tem certeza que deseja APAGAR TODAS as notificações? (s/n): ")
            if confirm.lower() == "s":
                resetarNotificacoes()
                print("\nTodas as notificações foram apagadas.")
            else:
                print("\nOperação cancelada.")

        elif opcao == "5":
            print("\nSaindo...")
            break

        else:
            print("\nOpção inválida. Tente novamente.")




## MENU RELATORIO
def menu_relatorio():
    while True:
        print("\n===== Menu Relatório =====")
        print("1. Gerar um relatório financeiro em um período específico")
        print("2. Gerar um comparativo entre dois anos completos")
        print("3. Sair")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            data_inicio_str = input("Escolha uma data de início (formato YYYY-MM-DD): ")
            data_fim_str = input("Escolha uma data de fim (formato YYYY-MM-DD): ")

            try:
                data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
                data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")
            except ValueError:
                print("Formato de data inválido. Use o formato YYYY-MM-DD.")
                continue

            periodo = {"data_inicio": data_inicio, "data_final": data_fim}

            response = gerar_relatorio_financeiro(periodo, True)
            if (response["Status"] == 200):
                print("\n📋 Relatório criado com sucesso!\n")
                pprint(response, sort_dicts=False)
                gerar_grafico_pizza_despesas(response)
            else:
                print("\nOcorreu um erro na elaboração do relatório.")

        elif opcao == "2":
            ano1 = int(input("Escolha um ano de início: "))
            ano2 = int(input("Escolha o ano de fim: "))
            response = gerar_comparativo(ano1, ano2, True)
            if (response["Status"] == 200):
                print("\nComparativo criado com sucesso:\n")
                pprint(response, sort_dicts=False)
            else:
                print("\nErro na elaboração do comparativo.")


        elif opcao == "3":
            print("\nSaindo...")
            break

        else:
            print("\nOpção inválida. Tente novamente.")

## MENU LANÇAMENTOS
def menu_lancamentos():
    while True:
        print("\n===== Menu Lançamentos Financeiros =====")
        print("1. Cadastrar lançamento")
        print("2. Editar lançamento")
        print("3. Remover lançamento")
        print("4. Listar lançamentos")
        print("5. Calcular saldo mensal")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            # Descrição
            while True:
                descricao = input("Descrição: ").strip()
                if descricao:
                    break
                else:
                    print("A descrição não pode ser vazia.")

            # Valor
            while True:
                valor_str = input("Valor: ").strip()
                try:
                    valor = float(valor_str)
                    if valor > 0:
                        break
                    else:
                        print("O valor deve ser maior que zero.")
                except ValueError:
                    print("Digite um valor numérico válido.")

            # Data
            while True:
                data_str = input("Data (YYYY-MM-DD): ").strip()
                try:
                    data = datetime.strptime(data_str, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Data inválida. Use o formato YYYY-MM-DD.")

            # Tipo
            while True:
                tipo = input("Tipo (receita/despesa): ").strip().lower()
                if tipo in ["receita", "despesa"]:
                    break
                else:
                    print("Tipo inválido. Digite 'receita' ou 'despesa'.")

            # Categoria
            while True:
                categoria = input("Categoria: ").strip()
                if categoria in categorias:
                    break
                else:
                    print(f"Categoria inválida! Escolha uma das seguintes: {categorias}")

            # Envio dos dados
            dados = {
                "descricao": descricao,
                "valor": valor,
                "data": data,
                "tipo": tipo,
                "categoria": categoria
            }

            response = criarLancamentoComPlanejamento(dados)
            print(response)


        elif opcao == "2":
            # ID do lançamento
            while True:
                id_str = input("ID do lançamento a editar: ").strip()
                if id_str.isdigit():
                    id_lanc = int(id_str)
                    break
                else:
                    print("ID inválido. Digite um número inteiro positivo.")

            # Descrição
            while True:
                descricao = input("Nova descrição: ").strip()
                if descricao:
                    break
                else:
                    print("A descrição não pode ser vazia.")

            # Valor
            while True:
                valor_str = input("Novo valor: ").strip()
                try:
                    valor = float(valor_str)
                    if valor > 0:
                        break
                    else:
                        print("O valor deve ser maior que zero.")
                except ValueError:
                    print("Digite um valor numérico válido.")

            # Data
            while True:
                data_str = input("Nova data (YYYY-MM-DD): ").strip()
                try:
                    data = datetime.strptime(data_str, "%Y-%m-%d")
                    break
                except ValueError:
                    print("Data inválida. Use o formato YYYY-MM-DD.")

            # Tipo
            while True:
                tipo = input("Novo tipo (receita/despesa): ").strip().lower()
                if tipo in ["receita", "despesa"]:
                    break
                else:
                    print("Tipo inválido. Digite 'receita' ou 'despesa'.")

            # Categoria
            while True:
                categoria = input("Nova categoria: ").strip()
                if categoria in categorias:
                    break
                else:
                    print(f"Categoria inválida! Escolha uma das seguintes: {categorias}")

            # Monta dados e edita
            novos_dados = {
                "descricao": descricao,
                "valor": valor,
                "data": data,
                "tipo": tipo,
                "categoria": categoria
            }

            response = editarLancamento(id_lanc, novos_dados)

            if "Success" in response:
                print("\nLançamento editado com sucesso.")
            else:
                print(f"\nErro ao editar: {response['Content']}")


        elif opcao == "3":
            # Remoção com validação do ID
            while True:
                id_str = input("ID do lançamento a remover: ").strip()
                if id_str.isdigit():
                    id_lanc = int(id_str)
                    break
                else:
                    print("ID inválido. Digite um número inteiro positivo.")

            response = removerLancamento(id_lanc)
            if "Success" in response:
                print("\n✅ Lançamento removido com sucesso.")
            else:
                print(f"\n❌ Erro: {response['Content']}")

        elif opcao == "4":
            print("\n🔍 Filtros opcionais (pressione Enter para ignorar):")

            filtros = {}

            # Valor
            valor = input("Valor: ").strip()
            if valor:
                try:
                    valor_float = float(valor)
                    if valor_float > 0:
                        filtros["valor"] = valor_float
                    else:
                        print("O valor deve ser positivo.")
                        continue
                except ValueError:
                    print("Valor inválido. Digite um número.")
                    continue

            # Data
            data_str = input("Data (YYYY-MM-DD): ").strip()
            if data_str:
                try:
                    filtros["data"] = datetime.strptime(data_str, "%Y-%m-%d")
                except ValueError:
                    print("Data inválida. Use o formato YYYY-MM-DD.")
                    continue

            # Tipo
            tipo = input("Tipo (receita/despesa): ").strip().lower()
            if tipo:
                if tipo not in ["receita", "despesa"]:
                    print("Tipo inválido. Digite 'receita' ou 'despesa'.")
                    continue
                filtros["tipo"] = tipo

            # Categoria
            categoria = input("Categoria: ").strip()
            if categoria:
                if categoria not in categorias:
                    print(f"Categoria inválida! Escolha uma das seguintes: {categorias}")
                    continue
                filtros["categoria"] = categoria

            # Consulta
            response = listarLancamentos(filtros)
            if "Success" in response:
                print("\n📄 Lançamentos encontrados:")
                for lanc in response["Content"]:
                    print(f"- ID {lanc['id']} | {lanc['descricao']} | R$ {lanc['valor']} | {lanc['data'].strftime('%Y-%m-%d')} | {lanc['tipo']} | {lanc['categoria']}")
            else:
                print(f"\n❌ {response['Content']}")

        elif opcao == "5":
            # Cálculo do saldo mensal
            while True:
                mes_str = input("Mês (1-12): ").strip()
                ano_str = input("Ano (ex: 2025): ").strip()
                try:
                    mes = int(mes_str)
                    ano = int(ano_str)
                    if 1 <= mes <= 12 and 1900 <= ano <= 2100:
                        break
                    else:
                        print("Mês ou ano fora do intervalo permitido.")
                except ValueError:
                    print("Digite números válidos para mês e ano.")

            response = calcularSaldoMensal(mes, ano)
            if "Success" in response:
                saldo = response["Content"]["saldo"]
                print(f"\n📊 Saldo de {mes:02d}/{ano}: R$ {saldo:.2f}")
            else:
                print(f"\n❌ {response['Content']}")

        elif opcao == "6":
            print("\n🚪 Saindo do menu de lançamentos...")
            break



def print_lancamentos(lancamentos):
    """
    Exibe uma lista de lançamentos financeiros de forma formatada no terminal.
    """
    if not lancamentos:
        print("Nenhum lançamento encontrado.")
        return
    print("\nID | Data       | Tipo     | Categoria      | Valor      | Descrição")
    print("-"*70)
    for l in lancamentos:
        data_str = l['data'].strftime('%Y-%m-%d') if hasattr(l['data'], 'strftime') else str(l['data'])
        print(f"{l['id']:>2} | {data_str} | {l['tipo']:<8} | {l['categoria']:<13} | R$ {l['valor']:>8.2f} | {l['descricao']}")


## MENU PLANEJAMENTO
def menu_planejamento():
    while True:
        print("\n===== Menu Planejamento Financeiro =====")
        print("1. Calcular divisão informando o salário")
        print("2. Calcular divisão a partir do último salário dos lançamentos")
        print("3. Visualizar divisão salva")
        print("4. Editar manualmente divisão de gastos")
        print("5. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            salario_str = input("Informe o salário base: ")
            try:
                salario = float(salario_str)
            except ValueError:
                print("Salário inválido.")
                continue

            resposta = calculaDivisaoGastos(salario)
            pprint(resposta)

        elif opcao == "2":
            resposta = calculaDivisaoDoUltimoSalario()
            pprint(resposta)

        elif opcao == "3":
            resposta = obterDivisaoSalva()
            pprint(resposta)

        elif opcao == "4":
            salario_str = input("Informe o salário total: ")
            try:
                salario = float(salario_str)
            except ValueError:
                print("Salário inválido.")
                continue

            divisao = {}
            print("Informe os valores para cada categoria:")
            categorias = [
                "moradia",
                "alimentacao",
                "transporte",
                "lazer",
                "saude",
                "educacao",
                "guardar"
            ]
            soma = 0.0
            for c in categorias:
                valor_str = input(f"{c.capitalize()}: ")
                try:
                    valor = float(valor_str)
                except ValueError:
                    print(f"Valor inválido para {c}.")
                    break
                divisao[c] = valor
                soma += valor
            else:
                if round(soma, 2) != round(salario, 2):
                    print(f"Soma dos valores ({soma}) difere do salário informado ({salario}).")
                    continue

                nova_divisao = {
                    "salario": salario,
                    "divisao": divisao
                }
                resposta = editarDivisaoGastos(nova_divisao)
                pprint(resposta)

        elif opcao == "5":
            print("Saindo do menu de planejamento...")
            break

        else:
            print("Opção inválida. Tente novamente.")



if __name__ == "__main__":
    while True:
        print("1. Notificação")
        print("2. Relatório financeiro")
        print("3. Lançamentos financeiros")
        print("4. Planejamento financeiro")
        print("5. Sair")

        opcao = input("Escolha uma categoria: ")

        if opcao == "1":
            menu_notificacoes(chat_id)
        elif opcao == "2":
            menu_relatorio()
        elif opcao == "3":
            menu_lancamentos()
        elif opcao == "4":
            menu_planejamento()
        else:
            print("\nSaindo do programa... Ciao!")
            break