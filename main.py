from modulos.notificacao import (
    listarNotificacoes,
    salvarNotificacao,
    enviarNotificacao,
)
from modulos.relatorio import (
    gerar_relatorio_financeiro,
    gerar_comparativo
)
from modulos.lancamento import (
    criarLancamento,
    editarLancamento,
    removerLancamento,
    listarLancamentos,
    calcularSaldoMensal
)

from modulos.relatorio.relatorio import gerar_grafico_pizza_despesas

from pprint import pprint #Para um pretty print no console
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
chat_id = 1665469613


## MENU NOTIFICACOES
def menu_notificacoes():
    while True:
        print("\n===== Menu Notificações =====")
        print("1. Listar notificações")
        print("2. Salvar notificação local")
        print("3. Enviar notificação para Telegram")
        print("4. Resetar notificações (APAGAR TUDO)")
        print("5. Sair")
        
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            response = listarNotificacoes()
            if "Success" in response:
                print("\n📋 Notificações:")
                for n in response["Content"]:
                    print(f"- {n['data']} : {n['conteudo']}")
            else:
                print("\nNenhuma notificação encontrada.")

        elif opcao == "2":
            conteudo = input("Digite o conteúdo da notificação: ")
            response = salvarNotificacao(conteudo)
            if "Success" in response:
                print("\nNotificação salva localmente.")
            else:
                print("\nErro ao salvar notificação.")

        elif opcao == "3":
            conteudo = input("Digite o conteúdo da notificação: ")

            response = enviarNotificacao(chat_id, conteudo)
            if "Success" in response:
                print("\nMensagem enviada para o Telegram e salva localmente.")
            else:
                print(f"\nErro: {response['Content']}")

        elif opcao == "4":
            confirm = input("Tem certeza que deseja APAGAR TODAS as notificações? (s/n): ")
            if confirm.lower() == "s":
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
        print("\n===== Menu Notificações =====")
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
            response = gerar_comparativo(ano1, ano2)
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
            descricao = input("Descrição: ")
            valor = float(input("Valor: "))
            data_str = input("Data (YYYY-MM-DD): ")
            tipo = input("Tipo (receita/despesa): ")
            categoria = input("Categoria: ")
            try:
                data = datetime.strptime(data_str, "%Y-%m-%d")
            except ValueError:
                print("Data inválida.")
                continue
            dados = {
                "descricao": descricao,
                "valor": valor,
                "data": data,
                "tipo": tipo,
                "categoria": categoria
            }
            response = criarLancamento(dados)
            print(response)

        elif opcao == "2":
            id_lanc = int(input("ID do lançamento a editar: "))
            descricao = input("Nova descrição: ")
            valor = float(input("Novo valor: "))
            data_str = input("Nova data (YYYY-MM-DD): ")
            tipo = input("Novo tipo (receita/despesa): ")
            categoria = input("Nova categoria: ")
            try:
                data = datetime.strptime(data_str, "%Y-%m-%d")
            except ValueError:
                print("Data inválida.")
                continue
            novos_dados = {
                "descricao": descricao,
                "valor": valor,
                "data": data,
                "tipo": tipo,
                "categoria": categoria
            }
            response = editarLancamento(id_lanc, novos_dados)
            print(response)

        elif opcao == "3":
            id_lanc = int(input("ID do lançamento a remover: "))
            response = removerLancamento(id_lanc)
            print(response)

        elif opcao == "4":
            print("Filtros opcionais (pressione Enter para ignorar):")
            valor = input("Valor: ")
            data_str = input("Data (YYYY-MM-DD): ")
            tipo = input("Tipo (receita/despesa): ")
            categoria = input("Categoria: ")
            filtros = {}
            if valor:
                try:
                    filtros["valor"] = float(valor)
                except ValueError:
                    print("Valor inválido.")
                    continue
            if data_str:
                try:
                    filtros["data"] = datetime.strptime(data_str, "%Y-%m-%d")
                except ValueError:
                    print("Data inválida.")
                    continue
            if tipo:
                filtros["tipo"] = tipo
            if categoria:
                filtros["categoria"] = categoria
            response = listarLancamentos(filtros)
            content = response.get("Content", None)
            if "Success" in response and isinstance(content, list):
                print("\nLançamentos encontrados:")
                print_lancamentos(content)
            elif isinstance(content, str):
                print(content)
            else:
                print("Nenhum lançamento encontrado ou erro desconhecido.")

        elif opcao == "5":
            mes = int(input("Mês (1-12): "))
            ano = int(input("Ano (ex: 2025): "))
            response = calcularSaldoMensal(mes, ano)
            print(response)

        elif opcao == "6":
            print("Saindo do menu de lançamentos...")
            break

        else:
            print("Opção inválida. Tente novamente.")


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


if __name__ == "__main__":
    while True:
        print("1. Notificação")
        print("2. Relatório financeiro")
        print("3. Lançamentos financeiros")
        print("4. Planejamento financeiro")
        print("5. Sair")

        opcao = input("Escolha uma categoria: ")

        if opcao == "1":
            menu_notificacoes()
        elif opcao == "2":
            menu_relatorio()
        elif opcao == "3":
            menu_lancamentos()
        else:
            print("\nSaindo do programa... Ciao!")
            break
    