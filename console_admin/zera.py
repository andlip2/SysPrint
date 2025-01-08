from sqlalchemy import create_engine, text
from datetime import datetime

# Configurações do banco de dados
db_url = "mysql+pymysql://app_user:sysprintusertest@192.168.1.226:3306/sysprint"
engine = create_engine(db_url)

def reset_all_users(messagebox):
    try:
        with engine.connect() as connection:
            # Zerar o contador para todos os usuários
            update_query = "UPDATE user_print_totals SET TotalPages = 0"
            connection.execute(text(update_query))
            connection.commit()

            # Registrar o reset no log
            insert_query = "INSERT INTO reset_log (LastReset) VALUES (:last_reset)"
            connection.execute(text(insert_query), {'last_reset': datetime.now()})
            connection.commit()

        messagebox.showinfo("Sucesso", "Contador de todos os usuários resetado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao resetar todos os usuários: {e}")

def reset_specific_user(user_id, messagebox):
    if not user_id:
        messagebox.showwarning("Aviso", "Por favor, insira o nome do usuário.")
        return

    try:
        with engine.connect() as connection:
            # Atualizando a consulta para usar a coluna 'user'
            update_query = "UPDATE user_print_totals SET TotalPages = 0 WHERE user = :user_id"
            rows_updated = connection.execute(text(update_query), {'user_id': user_id}).rowcount

            if rows_updated == 0:
                messagebox.showwarning("Aviso", f"Nenhum usuário encontrado com o nome '{user_id}'.")
            else:
                connection.commit()

                # Registrar o reset no log
                insert_query = "INSERT INTO reset_log (LastReset) VALUES (:last_reset)"
                connection.execute(text(insert_query), {'last_reset': datetime.now()})
                connection.commit()

                messagebox.showinfo("Sucesso", f"Contador do usuário '{user_id}' resetado com sucesso!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao resetar o usuário '{user_id}': {e}")
