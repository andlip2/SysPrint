from sqlalchemy import create_engine, text

# Configuração da conexão com o banco de dados (substitua pelos seus dados)
DB_URL = "mysql+pymysql://admin_user:admsysp%4025@192.168.1.226:3306/sysprint"
engine = create_engine(DB_URL)

def get_total_printed_pages(user):
    """Obtém o total de páginas impressas multiplicando Pages * Copies para um usuário específico."""
    select_query = """
    SELECT 
        SUM(Pages * Copies) AS TotalPrintedPages
    FROM 
        logs
    WHERE 
        User = :user
    """

    try:
        with engine.connect() as connection:
            result = connection.execute(text(select_query), {"user": user}).fetchone()
            
            if result and result[0] is not None:
                total_printed_pages = result[0]
                print(f"Total de páginas impressas por {user}: {total_printed_pages}")
            else:
                total_printed_pages = 0
                print(f"Usuário {user} não possui registros de impressão.")

            return total_printed_pages

    except Exception as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        return None

# Teste com um usuário específico
user_test = "anderson.filipe"
total_pages = get_total_printed_pages(user_test)
print(f"Páginas totais impressas para {user_test}: {total_pages}")
