import time
import csv
import os
import subprocess
from notification import show_notification
from sqlalchemy import create_engine, text
from datetime import datetime
import zera
import psutil
from win10toast import ToastNotifier
from block import monitor_print_limit
from listar_impressoras import listar_impressoras


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
    """Retorna o nome do usuário atualmente logado no Windows."""
    try:
        # Obter o usuário interativo logado
        for user in psutil.users():
            if user.name != "SYSTEM":  # Ignorar a conta SYSTEM
                logged_user = user.name
                print(f"Usuário logado atualmente: {logged_user}")
                return logged_user
        return None
    except Exception as e:
        print(f"Erro ao obter o usuário logado: {e}")
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


def create_tables():
    """Cria as tabelas 'logs' e 'user_print_totals' no banco de dados, sem sobrescrever dados existentes."""
    create_logs_table = """
    CREATE TABLE IF NOT EXISTS logs (
        Time DATETIME,
        User VARCHAR(255),
        Pages INT,
        Copies INT,
        Printer VARCHAR(255),
        DocumentName VARCHAR(255),
        Client VARCHAR(255),
        PaperSize VARCHAR(50),
        Language VARCHAR(50),
        Duplex VARCHAR(20),
        Grayscale VARCHAR(20),
        Size FLOAT,
        PRIMARY KEY (Time, User, DocumentName)
    ) ENGINE=InnoDB;
    """
    create_user_totals_table = f"""
    CREATE TABLE IF NOT EXISTS user_print_totals (
        User VARCHAR(255) PRIMARY KEY,
        TotalPages INT NOT NULL DEFAULT 0,
        PrintLimit INT NOT NULL DEFAULT {DEFAULT_PRINT_LIMIT},
        Blocked BOOLEAN NOT NULL DEFAULT FALSE
    ) ENGINE=InnoDB;
    """
    try:
        with engine.connect() as connection:
            print("Criando tabelas, se necessário...")
            connection.execute(text(create_logs_table))
            connection.execute(text(create_user_totals_table))
            print("Tabelas criadas ou já existentes.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")


def update_user_totals(user, pages):
    """Atualiza a tabela 'user_print_totals' com os totais de páginas por usuário e verifica o limite de impressão."""
    try:
        with engine.connect() as connection:
            # Iniciar transação
            transaction = connection.begin()

            # Verificar se o usuário já existe na tabela
            select_query = "SELECT TotalPages, PrintLimit, Blocked FROM user_print_totals WHERE User = :user"
            result = connection.execute(text(select_query), {"user": user}).fetchone()

            if result:
                # Se o usuário já existir, atualizar o total de páginas
                current_total = result[0]
                print_limit = result[1]
                blocked = result[2]
                new_total = current_total + pages

                # Verificar se o limite de impressão foi alcançado
                if new_total >= print_limit:
                    print(
                        f"Aviso: Limite de impressão excedido para o usuário {user}. Total de páginas: {new_total}."
                    )
                    # Atualizar a coluna 'Blocked' para TRUE
                    update_query = "UPDATE user_print_totals SET TotalPages = :new_total, Blocked = TRUE WHERE User = :user"
                    connection.execute(
                        text(update_query), {"new_total": new_total, "user": user}
                    )
                    stop_spooler_service_if_needed(user)  # Verificar e parar o Spooler
                else:
                    # Caso o limite não tenha sido alcançado, só atualiza o total de páginas
                    update_query = "UPDATE user_print_totals SET TotalPages = :new_total WHERE User = :user"
                    connection.execute(
                        text(update_query), {"new_total": new_total, "user": user}
                    )
                    print(f"Total de páginas atualizado para {user}: {new_total}")

            else:
                # Se o usuário não existir, inserir um novo registro com o limite de impressão e service_on = 0
                insert_query = """
                INSERT INTO user_print_totals (User, TotalPages, PrintLimit, Blocked, Service_on) 
                VALUES (:user, :pages, :print_limit, FALSE, TRUE)
                """
                connection.execute(
                    text(insert_query),
                    {"user": user, "pages": pages, "print_limit": DEFAULT_PRINT_LIMIT},
                )
                print(
                    f"Novo registro inserido para {user}: {pages} páginas, Limite de impressão: {DEFAULT_PRINT_LIMIT} páginas, Service_on: 0."
                )

            # Commit da transação
            transaction.commit()
    except Exception as e:
        print(f"Erro ao atualizar os totais de páginas para o usuário {user}: {e}")


def obter_impressoras_virtuais():
    """
    Retorna uma lista com os nomes de todas as impressoras virtuais encontradas.
    """
    impressoras = listar_impressoras()
    impressoras_virtuais = [
        impressora["Nome"] for impressora in impressoras if impressora["Tipo"] == "Virtual"
    ]
    return impressoras_virtuais

def comparar_impressoras(nome_impressora):
    """
    Compara o nome de uma impressora com a lista de impressoras virtuais.

    :param nome_impressora: Nome da impressora a ser comparada (string).
    :return: True se a impressora for virtual, False caso contrário.
    """
    # Obtém a lista de impressoras virtuais
    impressoras_virtuais = obter_impressoras_virtuais()
    # Remove espaços extras e realiza a comparação
    nome_impressora = nome_impressora.strip()
    if nome_impressora in impressoras_virtuais:
        return True
    else:
        return False
           
def insert_data_from_csv():
    """Lê o arquivo CSV e insere os dados no banco de dados, atualizando os totais."""
    try:
        with engine.connect() as connection:
            transaction = connection.begin()

            try:
                with open(csv_file_path, mode="r", encoding="latin1") as file:
                    reader = csv.reader(file)
                    next(reader)  # Ignorar a primeira linha
                    next(reader)  # Ignorar a segunda linha

                    for row in reader:
                        if row:
                            data = row[:12]
                            if len(data) == 12:
                                    time = data[0]
                                    user = data[1]
                                    pages = int(data[2]) if data[2].isdigit() else 0
                                    copies = int(data[3]) if data[3].isdigit() else 0
                                    printer = data[4]
                                    document_name = data[5]
                                    client = data[6]
                                    paper_size = data[7]
                                    language = data[8]
                                    duplex = data[9]
                                    grayscale = data[10]
                                    try:
                                        size = (
                                            float(data[11].replace("kb", "").strip())
                                            if "kb" in data[11]
                                            else 0.0
                                        )
                                    except ValueError:
                                        size = 0.0
                                    try:
                                        time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                                    except ValueError:
                                        time = None

                                    # Verificar duplicatas antes de inserir os dados
                                    select_query = """
                                    SELECT COUNT(*) FROM logs
                                    WHERE Time = :time AND User = :user AND DocumentName = :document_name
                                    """
                                    result = connection.execute(
                                        text(select_query),
                                        {
                                            "time": time,
                                            "user": user,
                                            "document_name": document_name,
                                        },
                                    ).scalar()
                                
                            virtual = comparar_impressoras(printer)
                            if not virtual:
                                    if result == 0:
                                        # Inserir dados na tabela 'logs'
                                        insert_query = """
                                        INSERT INTO logs (Time, User, Pages, Copies, Printer, DocumentName, Client, PaperSize, Language, Duplex, Grayscale, Size)
                                        VALUES (:time, :user, :pages, :copies, :printer, :document_name, :client, :paper_size, :language, :duplex, :grayscale, :size)
                                        """
                                        connection.execute(
                                            text(insert_query),
                                            {
                                                "time": time,
                                                "user": user,
                                                "pages": pages,
                                                "copies": copies,
                                                "printer": printer,
                                                "document_name": document_name,
                                                "client": client,
                                                "paper_size": paper_size,
                                                "language": language,
                                                "duplex": duplex,
                                                "grayscale": grayscale,
                                                "size": size,
                                            },
                                        )
                                        print(
                                            f"Dados inseridos para o documento: {document_name}"
                                        )
                                        print("Todos os dados foram inseridos com sucesso.")
                                        transaction.commit()

                                        # Atualizar totais de páginas
                                        if pages > 0:
                                            update_user_totals(user, pages)
                                    else:   
                                        print(
                                            f"Registro duplicado ignorado: {document_name}"
                                        )
                            else:
                                if virtual:
                                    print ( f"Impressora virtual: {printer}, ignorado adição")
                                else:
                                    print(f"Erro: Linha com dados insuficientes: {row}")
            except Exception as e:
                transaction.rollback()
                raise e
    except Exception as e:
        print(f"Erro ao processar o arquivo CSV ou inserir dados: {e}")

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
                        
                        
                        # Criar tabelas e processar dados
                        create_tables()
                        insert_data_from_csv()
                        usuario_logado = get_logged_in_user()
                        monitor_print_limit(usuario_logado)

                        # Verificação de reset
                        zera.run(engine)

                    else:
                        print(f"O serviço foi desativado para o usuário {user}. Saindo...")
                        break  # Sai do loop se Service_on for FALSE

                # Aguarda 1 segundos antes de verificar novamente
                time.sleep(1)

    except Exception as e:
        print(f"Erro ao verificar 'Service_on' para o usuário {user}: {e}")
        
verificar_service_on(get_logged_in_user())

