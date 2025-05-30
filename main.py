import time
import os
import subprocess
from notification import show_notification
from sqlalchemy import create_engine
from block import monitor_print_limit
from create_tables import create_tables
from carrega_csv import insert_data_from_csv
import wmi
from adiciona_departamento import update_department_limit

# URL de conexão com o banco
db_url = "mysql+pymysql://admin_user:admsysp%4025@192.168.1.226:3306/sysprint"
engine = create_engine(db_url)

# Caminho do arquivo CSV
csv_file_path = r"C:\\Program Files (x86)\\PaperCut Print Logger\\logs\\csv\\papercut-print-log-all-time.csv"

# Variável para o limite de impressão padrão
DEFAULT_PRINT_LIMIT = 0  # Difine limite padrão para usuario
Department_limit = 3000 # Difine limite padrão para o setor
departamento = "TI"

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


def verificar_service_on(user):
    """Verifica o status da coluna 'Service_on' para o usuário e executa ações se for TRUE."""
    try:
        while True:  # O loop continuará enquanto o Service_on for TRUE
            # Verificar o valor de 'Service_on' para o usuário
            service_on = True
            if service_on:
                print(
                    f"O serviço está ativado para o usuário {user}. Executando ação..."
                )

                usuario_logado = get_logged_in_user()
                # Criar tabelas e processar dados
                create_tables(DEFAULT_PRINT_LIMIT, engine)
                insert_data_from_csv(
                    DEFAULT_PRINT_LIMIT, engine, csv_file_path, usuario_logado
                )
                update_department_limit(departamento, Department_limit, engine)
                monitor_print_limit(user, usuario_logado, engine, DEFAULT_PRINT_LIMIT, departamento)

                # Pausa a execução por 1 segundos antes de repetir a verificação
                time.sleep(1)

            else:
                print(f"O serviço foi desativado para o usuário {user}. Saindo...")
                break  # Sai do loop se Service_on for FALSE

    except Exception as e:
        print(f"Erro ao verificar 'Service_on' para o usuário {user}: {e}")


verificar_service_on(get_logged_in_user())
