import subprocess
from sqlalchemy import create_engine, text

# Defina o motor do banco de dados
engine = create_engine("mysql+pymysql://admin_user:admsysp%4025@192.168.1.226:3306/sysprint")

def monitor_print_limit(user):
    """Verifica se o usuário atingiu o limite de impressão e atualiza o status 'Blocked' e inicia o serviço 'PCPrintLogger'."""
    try:
        with engine.connect() as connection:
            # Consulta para verificar as condições
            select_query = """
            SELECT User, TotalPages, PrintLimit, Blocked
            FROM user_print_totals
            WHERE User = :user
            """
            result = connection.execute(text(select_query), {"user": user}).fetchone()

            if result:
                # Desempacotando os resultados da consulta
                user, total_pages, print_limit, blocked = result

                print(f"TotalPages: {total_pages}, PrintLimit: {print_limit}, Blocked: {blocked}")

                # Verifica se o usuário atingiu o limite
                if total_pages >= print_limit:
                    print(f"Usuário {user} atingiu o limite de impressão ou já está desbloqueado.")
                    

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
                    print(f"Usuário {user} ainda não atingiu o limite de impressão.")
            else:
                print(f"Usuário {user} não encontrado na tabela.")

    except Exception as e:
        print(f"Erro ao verificar ou desbloquear o usuário {user}: {e}")
