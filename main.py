from modulos.notificacao.notificacao import (
    listarNotificacoes,
    salvarNotificacao,
    enviarNotificacao,
)
from modulos.relatorio import (
    gerar_relatorio_financeiro,
    gerar_comparativo
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



if __name__ == "__main__":
    while True:
        print("1. Notificação")
        print("2. Relatório financeiro")
        print("3. Planejamento financeiro")
        print("4. Principal")
        print("5. Sair")

        opcao = input("Escolha uma categoria: ")

        if opcao == "1":
            menu_notificacoes()

        elif opcao == "2":
            menu_relatorio()

        else:
            print("\nSaindo do programa... Ciao!")
            break
    