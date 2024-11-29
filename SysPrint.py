import csv
import os
from sqlalchemy import create_engine, text
from datetime import datetime

# URL de conexão com o banco
db_url = "mysql+pymysql://root:@localhost:3306/teste_rc"
engine = create_engine(db_url)

# Caminho do arquivo CSV
csv_file_path = r"C:\\Program Files (x86)\\PaperCut Print Logger\\logs\\csv\\papercut-print-log-all-time.csv"

# Verificar se o arquivo existe no caminho fornecido
if not os.path.isfile(csv_file_path):
    print(f"Erro: O arquivo {csv_file_path} não foi encontrado.")
else:
    print(f"Arquivo encontrado: {csv_file_path}")

def create_table():
    """Cria a tabela no banco de dados com uma chave primária para evitar duplicidade."""
    create_table_query = """
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
    try:
        with engine.connect() as connection:
            print("Tentando criar a tabela...")
            connection.execute(text(create_table_query))
            print("Tabela criada ou já existente.")
    except Exception as e:
        print(f"Erro ao criar a tabela: {e}")

def insert_data_from_csv():
    """Lê o arquivo CSV e insere os dados no banco de dados, evitando duplicidade."""
    try:
        with engine.connect() as connection:
            # Garantir que a transação será comprometida
            transaction = connection.begin()

            try:
                with open(csv_file_path, mode='r', encoding='latin1') as file:  # Usando encoding latin1
                    reader = csv.reader(file)
                    
                    # Ignorar as duas primeiras linhas
                    next(reader)  # Primeira linha (cabeçalho ou dados irrelevantes)
                    next(reader)  # Segunda linha
                    
                    for row in reader:
                        if row:  # Verifica se a linha não está vazia
                            # Limitar aos primeiros 12 campos
                            data = row[:12]  # Pega apenas os 12 primeiros campos
                            
                            # Verificar se a linha tem o número de campos esperado
                            if len(data) == 12:
                                # Extração de dados da linha
                                time = data[0]
                                user = data[1]
                                pages = int(data[2]) if data[2].isdigit() else 0
                                copies = int(data[3]) if data[3].isdigit() else 0
                                printer = data[4]
                                document_name = data[5]
                                client = data[6]
                                paper_size = data[7]
                                language = data[8]
                                duplex = data[9]  # Mantém como string
                                grayscale = data[10]  # Mantém como string
                                
                                # Tentar processar o tamanho; tratar campos inválidos
                                try:
                                    size = float(data[11].replace('kb', '').strip()) if 'kb' in data[11] else 0.0
                                except ValueError:
                                    size = 0.0
                                
                                # Conversão de time para datetime
                                try:
                                    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')  # Ajuste o formato conforme necessário
                                except ValueError:
                                    time = None
                                
                                # Verificar se o registro já existe
                                select_query = """
                                SELECT COUNT(*) FROM logs
                                WHERE Time = :time AND User = :user AND DocumentName = :document_name
                                """
                                result = connection.execute(text(select_query), {
                                    'time': time,
                                    'user': user,
                                    'document_name': document_name
                                }).scalar()
                                
                                if result == 0:  # Insere apenas se não existir
                                    insert_query = """
                                    INSERT INTO logs (Time, User, Pages, Copies, Printer, DocumentName, Client, PaperSize, Language, Duplex, Grayscale, Size)
                                    VALUES (:time, :user, :pages, :copies, :printer, :document_name, :client, :paper_size, :language, :duplex, :grayscale, :size)
                                    """
                                    connection.execute(text(insert_query), {
                                        'time': time,
                                        'user': user,
                                        'pages': pages,
                                        'copies': copies,
                                        'printer': printer,
                                        'document_name': document_name,
                                        'client': client,
                                        'paper_size': paper_size,
                                        'language': language,
                                        'duplex': duplex,
                                        'grayscale': grayscale,
                                        'size': size
                                    })
                                    print(f"Dados inseridos para o documento: {document_name}")
                                else:
                                    print(f"Registro duplicado ignorado: {document_name}")
                            else:
                                print(f"Erro: A linha não contém dados suficientes (menos de 12 campos). Linha: {row}")
                
                # Commit da transação
                transaction.commit()
                print("Todos os dados foram inseridos com sucesso.")
            except Exception as e:
                transaction.rollback()  # Reverter em caso de erro
                raise e
    except Exception as e:
        print(f"Erro ao processar o arquivo CSV ou inserir dados: {e}")

# Criação da tabela no banco de dados
create_table()

# Inserir dados do arquivo CSV no banco de dados
insert_data_from_csv()
