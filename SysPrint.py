import csv
import os
import subprocess
from sqlalchemy import create_engine, text
from datetime import datetime

# URL de conexão com o banco
db_url = "mysql+pymysql://root:sysprintdb@localhost:3306/logs_impressoras"
engine = create_engine(db_url)

# Caminho do arquivo CSV
csv_file_path = r"C:\\Program Files (x86)\\PaperCut Print Logger\\logs\\csv\\papercut-print-log-all-time.csv"

# Variável para o limite de impressão padrão
DEFAULT_PRINT_LIMIT = 300  # Altere este valor conforme necessário

# Verificar se o arquivo existe
if not os.path.isfile(csv_file_path):
    print(f"Erro: O arquivo {csv_file_path} não foi encontrado.")
else:
    print(f"Arquivo encontrado: {csv_file_path}")


def stop_spooler_service():
    """Interrompe o serviço do Spooler de Impressão e seus dependentes."""
    try:
        print("Parando serviços dependentes do Spooler de Impressão...")
        # Parar o Spooler e todos os serviços dependentes
        subprocess.run(["sc", "stop", "spooler"], check=True, text=True, shell=True)
        print("Serviço do Spooler de Impressão interrompido com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao tentar parar o Spooler de Impressão: {e}")
        print(
            "Certifique-se de que o script está sendo executado com permissões de administrador."
        )


def create_tables():
    """Cria as tabelas 'logs' e 'user_print_totals' no banco de dados."""
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
        PrintLimit INT NOT NULL DEFAULT {DEFAULT_PRINT_LIMIT}
    ) ENGINE=InnoDB;
    """
    create_reset_table = """
    CREATE TABLE IF NOT EXISTS reset_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        last_reset_month DATE
    ) ENGINE=InnoDB;
    """
    try:
        with engine.connect() as connection:
            print("Criando tabelas...")
            connection.execute(text("DROP TABLE IF EXISTS logs"))
            connection.execute(text("DROP TABLE IF EXISTS user_print_totals"))
            connection.execute(text("DROP TABLE IF EXISTS reset_info"))
            connection.execute(text(create_logs_table))
            connection.execute(text(create_user_totals_table))
            connection.execute(text(create_reset_table))
            print("Tabelas criadas ou já existentes.")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")


def check_and_reset_totals():
    """Verifica se o mês foi alterado e reseta os contadores de impressão."""
    try:
        with engine.connect() as connection:
            # Obter o mês atual
            current_month = datetime.now().strftime("%Y-%m")

            # Verificar a data do último reset
            select_query = (
                "SELECT last_reset_month FROM reset_info ORDER BY id DESC LIMIT 1"
            )
            result = connection.execute(text(select_query)).fetchone()

            if result:
                last_reset_month = result[0].strftime("%Y-%m")
            else:
                last_reset_month = None

            # Se o mês atual for diferente do mês do último reset, resetar os contadores
            if last_reset_month != current_month:
                # Resetar os totais de impressão
                print("Novo mês detectado. Resetando contadores de impressão...")

                # Zerar os totais de impressão
                update_query = "UPDATE user_print_totals SET TotalPages = 0"
                connection.execute(text(update_query))
                print("Totais de impressão resetados para todos os usuários.")

                # Registrar o reset do mês
                insert_reset_query = (
                    "INSERT INTO reset_info (last_reset_month) VALUES (:current_month)"
                )
                connection.execute(
                    text(insert_reset_query), {"current_month": current_month}
                )
                print(f"Data do reset registrada: {current_month}")
            else:
                print("O mês ainda não foi alterado. Nenhum reset necessário.")

    except Exception as e:
        print(f"Erro ao verificar ou resetar os totais: {e}")


def update_user_totals(user, pages):
    """Atualiza a tabela 'user_print_totals' com os totais de páginas por usuário e verifica o limite de impressão."""
    try:
        with engine.connect() as connection:
            # Iniciar transação
            transaction = connection.begin()

            # Verificar se o usuário já existe na tabela
            select_query = "SELECT TotalPages, PrintLimit FROM user_print_totals WHERE User = :user"
            result = connection.execute(text(select_query), {"user": user}).fetchone()

            if result:
                # Se o usuário já existir, atualizar o total de páginas
                current_total = result[0]
                print_limit = result[1]
                new_total = current_total + pages

                # Verificar se o limite de impressão foi alcançado
                if new_total > print_limit:
                    print(
                        f"Aviso: Limite de impressão excedido para o usuário {user}. Total de páginas: {new_total}."
                    )
                    stop_spooler_service()  # Interromper o Spooler de Impressão
                    new_total = (
                        print_limit  # Opcional: bloqueia o total no limite máximo
                    )

                update_query = "UPDATE user_print_totals SET TotalPages = :new_total WHERE User = :user"
                connection.execute(
                    text(update_query), {"new_total": new_total, "user": user}
                )
                print(f"Total de páginas atualizado para {user}: {new_total}")
            else:
                # Se o usuário não existir, inserir um novo registro com o limite de impressão
                insert_query = """
                INSERT INTO user_print_totals (User, TotalPages, PrintLimit) VALUES (:user, :pages, :print_limit)
                """
                connection.execute(
                    text(insert_query),
                    {"user": user, "pages": pages, "print_limit": DEFAULT_PRINT_LIMIT},
                )
                print(
                    f"Novo registro inserido para {user}: {pages} páginas, Limite de impressão: {DEFAULT_PRINT_LIMIT} páginas."
                )

            # Commit da transação
            transaction.commit()
    except Exception as e:
        print(f"Erro ao atualizar os totais de páginas para o usuário {user}: {e}")


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

                                # Verificar duplicatas
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

                                if result == 0:
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

                                    # Atualizar totais de páginas
                                    if pages > 0:
                                        update_user_totals(user, pages)
                                else:
                                    print(
                                        f"Registro duplicado ignorado: {document_name}"
                                    )
                            else:
                                print(f"Erro: Linha com dados insuficientes: {row}")
                transaction.commit()
                print("Todos os dados foram inseridos com sucesso.")
            except Exception as e:
                transaction.rollback()
                raise e
    except Exception as e:
        print(f"Erro ao processar o arquivo CSV ou inserir dados: {e}")


# Criar tabelas e processar dados
create_tables()
check_and_reset_totals()  # Verificar e resetar os totais de impressão, se necessário
insert_data_from_csv()
