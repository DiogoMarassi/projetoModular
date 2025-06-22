from modulos.notificacao import (
    listarNotificacoes,
    salvarNotificacao,
    enviarNotificacao,
)
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
chat_id = "1665469613"

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

if __name__ == "__main__":
    menu_notificacoes()
