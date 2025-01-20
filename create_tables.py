from sqlalchemy import text


def create_tables(DEFAULT_PRINT_LIMIT, engine):
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