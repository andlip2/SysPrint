from sqlalchemy import text


def update_user_totals(user, pages, DEFAULT_PRINT_LIMIT, engine, departamento):
    """Atualiza a tabela 'users' com os totais de páginas por usuário e verifica o limite de impressão."""
    try:
        with engine.connect() as connection:
            # Iniciar transação
            transaction = connection.begin()

            # Verificar se o usuário já existe na tabela
            select_query = "SELECT PrintLimit, Blocked FROM users WHERE User = :user"
            result = connection.execute(text(select_query), {"user": user}).fetchone()

            if result:
                print(f"Usuário {user} já registrado no sistema.")

            else:
                # Se o usuário não existir, inserir um novo registro com o limite de impressão e service_on = 0
                insert_query = """
                INSERT INTO users (User, PrintLimit, Blocked, Department) 
                VALUES (:user, :print_limit, FALSE, :department)
                """
                connection.execute(
                    text(insert_query),
                    {
                        "user": user,
                        "print_limit": DEFAULT_PRINT_LIMIT,
                        "department": departamento,
                    },
                )
                print(
                    f"Novo registro inserido para {user}: Limite de impressão: {DEFAULT_PRINT_LIMIT}, Departamento: {departamento}."
                )

            # Commit da transação
            transaction.commit()
    except Exception as e:
        print(f"Erro ao atualizar os dados para o usuário {user}: {e}")
