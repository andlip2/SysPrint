from sqlalchemy import text
from para_spooler import stop_spooler_service_if_needed


def update_user_totals(user, pages, DEFAULT_PRINT_LIMIT, engine, user_logado):
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
                    stop_spooler_service_if_needed(user, user_logado)  # Verificar e parar o Spooler
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