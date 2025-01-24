import subprocess
from sqlalchemy import text
from stop_spooler import stop_spooler_service_if_needed
from atualiza_user import update_user_totals

def monitor_print_limit(user, usuario_logado, engine, DEFAULT_PRINT_LIMIT, departamento):
    """Verifica se o usuário atingiu o limite de impressão e atualiza o status 'Blocked' e inicia o serviço 'PCPrintLogger'."""
    try:
        with engine.connect() as connection:
            # Consulta para verificar as condições dentro do mês atual
            select_query = """
            SELECT 
                u.User, 
                SUM(l.Pages * l.Copies) AS totalPages, 
                u.PrintLimit, 
                u.Blocked,
                u.Department
            FROM 
                users u
            JOIN 
                logs l ON u.User = l.User
            WHERE 
                u.User = :user
                AND DATE_FORMAT(STR_TO_DATE(l.Time, '%Y-%m-%d'), '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')
            GROUP BY 
                u.User, u.PrintLimit, u.Blocked, u.Department
            """

            result = connection.execute(text(select_query), {"user": user}).fetchone()

            # Inicializa variáveis com valores padrão
            total_pages = 0
            print_limit = DEFAULT_PRINT_LIMIT
            blocked = 0
            department = departamento

            if result:
                # Desempacotando os resultados da consulta
                user, total_pages, print_limit, blocked, department = result

                print(
                    f"TotalPages: {total_pages}, PrintLimit: {print_limit}, Blocked: {blocked}, Departamento: {department}"
                )

            # Se o PrintLimit for 0, buscar o TotalLimit do departamento
            if print_limit == 0:
                department_limit_query = """
                SELECT TotalLimit FROM department_limits WHERE Department = :department
                """
                department_limit_result = connection.execute(
                    text(department_limit_query), {"department": department}
                ).fetchone()

                if department_limit_result:
                    total_limit = department_limit_result[0]  # Corrigido para acessar via índice
                    print(f"Usando limite do departamento {department}: {total_limit}")

                    # Se o limite do departamento também for 0, então não há restrição de impressão
                    if total_limit == 0:
                        print(f"Departamento {department} com limite infinito.")
                        total_limit = float('inf')  # Define um limite infinito para não bloquear o usuário
                else:
                    raise ValueError(f"Limite para o departamento {department} não encontrado.")

            else:
                total_limit = print_limit

            # Atualiza os totais independentemente de haver resultado na consulta ou não
            update_user_totals(user, total_pages, DEFAULT_PRINT_LIMIT, engine, department)

            if total_pages >= total_limit:
                print(
                    f"Usuário {user} atingiu o limite de impressão ou já está bloqueado."
                )
                stop_spooler_service_if_needed(user, usuario_logado)
            else:
                print(f"Usuário {user} ainda não atingiu o limite de impressão.")
                # Atualizar a coluna 'Blocked' para 0
                update_query = """
                    UPDATE users
                    SET Blocked = 0
                    WHERE User = :user
                    """
                connection.execute(text(update_query), {"user": user})

                # Iniciar o serviço 'PCPrintLogger'
                subprocess.run(
                    ["sc", "start", "PCPrintLogger"], check=True, text=True, shell=True
                )
                print(
                    f"Serviço 'PCPrintLogger' iniciado com sucesso para o usuário {user}."
                )

    except Exception as e:
        print(f"Erro ao verificar ou desbloquear o usuário {user}: {e}")
