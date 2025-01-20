import time
import os
import subprocess
from notification import show_notification
from sqlalchemy import create_engine, text
import zera
from block import monitor_print_limit
from create_tables import create_tables
from carrega_csv import insert_data_from_csv
import wmi

# URL de conexão com o banco
db_url = "mysql+pymysql://admin_user:admsysp%4025@192.168.1.226:3306/sysprint"
engine = create_engine(db_url)

# Caminho do arquivo CSV
csv_file_path = r"C:\\Program Files (x86)\\PaperCut Print Logger\\logs\\csv\\papercut-print-log-all-time.csv"

# Variável para o limite de impressão padrão
DEFAULT_PRINT_LIMIT = 3000  # Altere este valor conforme necessário

# Verificar se o arquivo existe
if not os.path.isfile(csv_file_path):
    print(f"Erro: O arquivo {csv_file_path} não foi encontrado.")
else:
    print(f"Arquivo encontrado: {csv_file_path}")


def get_logged_in_user():
    try:
        c = wmi.WMI()
        for session in c.Win32_ComputerSystem():
            username = session.UserName
            if username:
                # Divide a string pelo caractere '\' e pega apenas o nome de usuário
                user = username.split("\\")[-1]
                print(f"Usuário ativo atualmente: {user}")
                return user
        return None
    except Exception as e:
        print(f"Erro ao obter o usuário ativo: {e}")
        return None

# Para o serviço de spooler e verifica o
def stop_spooler_service_if_needed(user):
    """
    Interrompe o serviço do Spooler de Impressão se o usuário
    que atingiu o limite for o mesmo que está logado.
    """
    logged_in_user = get_logged_in_user()
    print(
        f"Usuário logado: {logged_in_user}\nUsuário que atingiu o limite de impressões {user}"
    )

    if logged_in_user and logged_in_user.lower() == user.lower():
        try:
            print(
                f"Usuário {user} atingiu o limite de impressão e está logado. Interrompendo o Spooler..."
            )

            # Mostra a notificação do windows
            print("Chamando not")
            show_notification(
                "Limite de impressões atingido",
                f"O usuário {user} atingiu o limite de impressões e foi bloqueado.",
                duration=15,
            )

            time.sleep(5)

            subprocess.run(
                ["sc", "stop", "PCPrintLogger"], check=True, text=True, shell=True
            )
            subprocess.run(["sc", "stop", "spooler"], check=True, text=True, shell=True)
            print("Serviço do Spooler de Impressão interrompido com sucesso.")

        except subprocess.CalledProcessError as e:
            print(f"Erro ao tentar parar o Spooler de Impressão: {e}")
            print(
                "Certifique-se de que o script está sendo executado com permissões de administrador."
            )
    else:
        print(
            f"Usuário {user} atingiu o limite, mas não está logado. O Spooler continuará funcionando."
        )

def verificar_service_on(user):
    """Verifica o status da coluna 'Service_on' para o usuário e executa ações se for TRUE."""
    try:
        with engine.connect() as connection:
            while True:  # O loop continuará enquanto o Service_on for TRUE
                # Verificar o valor de 'Service_on' para o usuário
                select_query = "SELECT Service_on FROM user_print_totals WHERE User = :user"
                result = connection.execute(text(select_query), {"user": user}).fetchone()

                if result:
                    service_on = result[0]
                    if service_on:
                        print(f"O serviço está ativado para o usuário {user}. Executando ação...") 
                        
                        usuario_logado = get_logged_in_user()
                        # Criar tabelas e processar dados
                        create_tables(DEFAULT_PRINT_LIMIT, engine)
                        insert_data_from_csv(DEFAULT_PRINT_LIMIT, engine, csv_file_path, usuario_logado)
                        monitor_print_limit(user, usuario_logado, engine)

                        # Verificação de reset
                        zera.run(engine)

                    else:
                        print(f"O serviço foi desativado para o usuário {user}. Saindo...")
                        break  # Sai do loop se Service_on for FALSE

                # Aguarda 1 segundos antes de verificar novamente
                time.sleep(100)

    except Exception as e:
        print(f"Erro ao verificar 'Service_on' para o usuário {user}: {e}")
        
verificar_service_on(get_logged_in_user())

