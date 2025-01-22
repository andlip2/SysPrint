import subprocess
from sqlalchemy import text
from stop_spooler import stop_spooler_service_if_needed
from sqlalchemy import text
import subprocess
from atualiza_user import update_user_totals


def monitor_print_limit(user, usuario_logado, engine, DEFAULT_PRINT_LIMIT):
    """Verifica se o usuário atingiu o limite de impressão e atualiza o status 'Blocked' e inicia o serviço 'PCPrintLogger'."""
    try:
        with engine.connect() as connection:
            # Consulta para verificar as condições dentro do mês atual
            select_query = """
            SELECT 
                u.User, 
                SUM(l.Pages * l.Copies) AS totalPages, 
                u.PrintLimit, 
                u.Blocked
            FROM 
                user_print_totals u
            JOIN 
                logs l ON u.User = l.User
            WHERE 
                u.User = :user
                AND DATE_FORMAT(STR_TO_DATE(l.Time, '%Y-%m-%d'), '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')
            GROUP BY 
                u.User, u.PrintLimit, u.Blocked
            """

            result = connection.execute(text(select_query), {"user": user}).fetchone()

            if result:
                # Desempacotando os resultados da consulta
                user, total_pages, print_limit, blocked = result

                print(f"TotalPages: {total_pages}, PrintLimit: {print_limit}, Blocked: {blocked}")
                
                update_user_totals(user, total_pages, DEFAULT_PRINT_LIMIT, engine)

                # Verifica se o usuário atingiu o limite
                if total_pages >= print_limit:
                    print(f"Usuário {user} atingiu o limite de impressão ou já está bloqueado.")
                    stop_spooler_service_if_needed(user, usuario_logado)
                else:
                    print(f"Usuário {user} ainda não atingiu o limite de impressão.")
                    # Atualizar a coluna 'Blocked' para 0
                    update_query = """
                        UPDATE user_print_totals
                        SET Blocked = 0
                        WHERE User = :user
                        """
                    connection.execute(text(update_query), {"user": user})

                    # Iniciar o serviço 'PCPrintLogger'
                    subprocess.run(
                        ["sc", "start", "PCPrintLogger"], check=True, text=True, shell=True
                    )
                    print(f"Serviço 'PCPrintLogger' iniciado com sucesso para o usuário {user}.")
            else:
                print(f"Usuário {user} não encontrado na tabela.")
                update_user_totals(user, DEFAULT_PRINT_LIMIT, engine)

    except Exception as e:
        print(f"Erro ao verificar ou desbloquear o usuário {user}: {e}")

        
