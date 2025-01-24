import csv
from sqlalchemy import text
from datetime import datetime
from atualiza_user import update_user_totals
from listar_impressoras import comparar_impressoras

#Insere dados do CSV para o banco de dados           
def insert_data_from_csv(DEFAULT_PRINT_LIMIT, engine, csv_file_path, user_logado):
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