import os
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# URL de conexão com o banco
db_url = "mysql+pymysql://root:@localhost:3306/teste_rc"
engine = create_engine(db_url)

# Função para criar a tabela 'reset_log' e inserir a data de hoje, caso a tabela esteja vazia
def create_reset_log_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS reset_log (
        LastReset DATETIME NOT NULL
    ) ENGINE=InnoDB;
    """
    try:
        with engine.connect() as connection:
            # Criar a tabela, caso não exista
            connection.execute(text(create_table_query))
            print("Tabela 'reset_log' criada ou já existente.")

            # Verificar se a tabela está vazia e inserir a data de hoje, se necessário
            select_query = "SELECT COUNT(*) FROM reset_log"
            count_result = connection.execute(text(select_query)).scalar()

            if count_result == 0:
                # Inserir a data de hoje se não houver registros
                insert_query = """
                INSERT INTO reset_log (LastReset) 
                VALUES (:last_reset)
                """
                connection.execute(text(insert_query), {'last_reset': datetime.now()})
                print(f"Data de reset inicial inserida: {datetime.now()}")
                connection.commit()  # Commit manual após inserção
            else:
                print("A tabela já contém registros.")
    except Exception as e:
        print(f"Erro ao criar a tabela 'reset_log': {e}")

# Função para verificar se é hora de resetar o contador de páginas
def should_reset_counter():
    try:
        with engine.connect() as connection:
            # Consultar a última execução do reset
            select_query = "SELECT LastReset FROM reset_log ORDER BY LastReset DESC LIMIT 1"
            result = connection.execute(text(select_query)).fetchone()

            if result:
                last_reset = result[0]
                # Verificar se já passou 24 horas desde o último reset
                if last_reset and datetime.now() - last_reset >= timedelta(minutes=1):
                    return True
            else:
                # Se não houver registro, considera que precisa resetar (primeira execução)
                return True
    except Exception as e:
        print(f"Erro ao verificar a última execução do reset: {e}")
    return False

# Função para zerar o contador de páginas
def reset_page_counter():
    try:
        with engine.connect() as connection:
            # Zerar o contador de páginas
            update_query = "UPDATE user_print_totals SET TotalPages = 0"
            connection.execute(text(update_query))
            print("Contador de páginas resetado com sucesso.")

            # Registrar a execução do reset
            insert_query = """
            INSERT INTO reset_log (LastReset) 
            VALUES (:last_reset)
            """
            # Passando a data e hora corretamente
            connection.execute(text(insert_query), {'last_reset': datetime.now()})
            connection.commit()  # Commit manual após inserção
            print(f"Data de reset registrada: {datetime.now()}")

    except Exception as e:
        print(f"Erro ao resetar o contador de páginas: {e}")

# Executar o script
def run():
    create_reset_log_table()  # Criar a tabela, se necessário
    if should_reset_counter():
        reset_page_counter()
    else:
        print("Ainda não é hora de resetar o contador.")

# Rodar o script
run()
