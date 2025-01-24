from sqlalchemy import text


def update_user_totals(user, pages, DEFAULT_PRINT_LIMIT, engine, departamento):
    """Atualiza a tabela 'users' com os totais de páginas por usuário e verifica o limite de impressão."""
    try:
        with engine.connect() as connection:
            # Iniciar transação
            transaction = connection.begin()

            # Verificar se o usuário já existe na tabela
            select_query = (
                "SELECT TotalPages, PrintLimit, Blocked FROM users WHERE User = :user"
            )
            result = connection.execute(text(select_query), {"user": user}).fetchone()

            if result:
                # Se o usuário já existir, atualizar o total de páginas
                new_total = pages

                # Caso o limite não tenha sido alcançado, só atualiza o total de páginas
                update_query = (
                    "UPDATE users SET TotalPages = :new_total WHERE User = :user"
                )
                connection.execute(
                    text(update_query), {"new_total": new_total, "user": user}
                )
                print(f"Total de páginas atualizado para {user}: {new_total}")

            else:
                # Se o usuário não existir, inserir um novo registro com o limite de impressão e service_on = 0
                insert_query = """
                INSERT INTO users (User, TotalPages, PrintLimit, Blocked, Department) 
                VALUES (:user, :pages, :print_limit, FALSE, :department)
                """
                connection.execute(
                    text(insert_query),
                    {"user": user, "pages": pages, "print_limit": DEFAULT_PRINT_LIMIT, "department": departamento},
                )
                print(
                    f"Novo registro inserido para {user}: {pages} páginas, Limite de impressão: {DEFAULT_PRINT_LIMIT} páginas departamento: {departamento}."
                )

            # Commit da transação
            transaction.commit()
    except Exception as e:
        print(f"Erro ao atualizar os totais de páginas para o usuário {user}: {e}")



