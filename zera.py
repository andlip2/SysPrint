import os
import json
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# Arquivo de configuração
config_file = "last_reset.json"

# Intervalo para o reset
RESET_INTERVAL = timedelta(days=30)

# Função para reiniciar serviços do Windows
def restart_service(service_name):
    try:
        print(f"Parando o serviço '{service_name}'...")
        os.system(f"net stop {service_name}")
        print(f"Iniciando o serviço '{service_name}'...")
        os.system(f"net start {service_name}")
        print(f"Serviço '{service_name}' reiniciado com sucesso.")
    except Exception as e:
        print(f"Erro ao reiniciar o serviço '{service_name}': {e}")


# Função para criar a tabela 'reset_log' e inserir a data de hoje, caso a tabela esteja vazia
def create_reset_log_table(connection):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS reset_log (
        LastReset DATETIME NOT NULL
    ) ENGINE=InnoDB;
    """
    try:
        connection.execute(text(create_table_query))
        print("Tabela 'reset_log' criada ou já existente.")

        select_query = "SELECT COUNT(*) FROM reset_log"
        count_result = connection.execute(text(select_query)).scalar()

        if count_result == 0:
            insert_query = """
            INSERT INTO reset_log (LastReset) 
            VALUES (:last_reset)
            """
            connection.execute(text(insert_query), {"last_reset": datetime.now()})
            print(f"Data de reset inicial inserida: {datetime.now()}")
            connection.commit()
        else:
            print("A tabela já contém registros.")
    except Exception as e:
        print(f"Erro ao criar a tabela 'reset_log': {e}")


# Função para verificar se é hora de resetar o contador de páginas
def should_reset_counter(connection):
    try:
        # Consultar a última execução do reset
        select_query = "SELECT LastReset FROM reset_log ORDER BY LastReset DESC LIMIT 1"
        result = connection.execute(text(select_query)).fetchone()

        if result:
            last_reset = result[0]
            # Verificar se já passou o intervalo de 30 dias desde o último reset
            if last_reset and datetime.now() - last_reset >= RESET_INTERVAL:
                return True
        else:
            # Se não houver registro, considera que precisa resetar (primeira execução)
            return True
    except Exception as e:
        print(f"Erro ao verificar a última execução do reset: {e}")
    return False


# Função para zerar o contador de páginas
def reset_page_counter(connection):
    try:
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
        connection.execute(text(insert_query), {"last_reset": datetime.now()})
        connection.commit()  # Commit manual após inserção
        print(f"Data de reset registrada: {datetime.now()}")

        # Reiniciar serviços necessários
        restart_service("spooler")         # Reinicia o spooler de impressão
        restart_service("PCPrintLogger")  # Reinicia o serviço PCPrintLogger

    except Exception as e:
        print(f"Erro ao resetar o contador de páginas: {e}")


def load_config():
    # Carrega as configurações do arquivo JSON.
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver corrompido, retorna configuração padrão
        return {"last_reset": None}


def save_config(config):
    # Salva as configurações no arquivo JSON.
    with open(config_file, "w") as file:
        json.dump(config, file, indent=4)


def check_and_reset(connection):
    """Verifica se o tempo para reset passou e executa o reset se necessário."""
    config = load_config()

    last_reset_str = config.get("last_reset")
    if last_reset_str:
        last_reset = datetime.fromisoformat(last_reset_str)
    else:
        last_reset = None

    # Se o último reset foi feito e o intervalo de 30 dias passou
    if last_reset and datetime.now() - last_reset >= RESET_INTERVAL:
        print("Intervalo de 30 dias alcançado, realizando reset...")
        reset_page_counter(connection)  # Chama a função que zera os valores

        # Atualiza a data do último reset
        config["last_reset"] = datetime.now().isoformat()
        save_config(config)  # Salva a configuração com a nova data
    else:
        print("Ainda não é hora de resetar o contador.")


# Executar o script
def run(engine):
    # Estabelecendo a conexão com o banco
    with engine.connect() as connection:
        create_reset_log_table(connection)  # Criar a tabela, se necessário
        check_and_reset(connection)  # Verificar e possivelmente resetar o contador
