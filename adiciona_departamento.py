from sqlalchemy import text


def update_department_limit(department, total_limit, engine):
    """Atualiza a tabela 'department_limits' com o limite total de impressão para o departamento."""
    try:
        with engine.connect() as connection:
            # Iniciar transação
            transaction = connection.begin()

            # Verificar se o departamento já existe na tabela
            select_query = "SELECT TotalLimit FROM department_limits WHERE Department = :department"
            result = connection.execute(
                text(select_query), {"department": department}
            ).fetchone()

            if not result:
                
                # Se o departamento não existir, inserir um novo registro
                insert_query = """
                INSERT INTO department_limits (Department, TotalLimit)
                VALUES (:department, :total_limit)
                """
                connection.execute(
                    text(insert_query),
                    {"department": department, "total_limit": total_limit},
                )
                print(
                    f"Novo registro inserido para o departamento {department}: Limite de impressão: {total_limit}"
                )

            # Commit da transação
            transaction.commit()

    except Exception as e:
        print(
            f"Erro ao atualizar o limite de impressão para o departamento {department}: {e}"
        )


