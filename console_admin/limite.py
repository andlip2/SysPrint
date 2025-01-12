from sqlalchemy import create_engine, text
from PyQt5.QtWidgets import QMessageBox

# Configurações do banco de dados
db_url = "mysql+pymysql://app_user:sysprintusertest@192.168.1.226:3306/sysprint"
engine = create_engine(db_url)

def set_user_limit(user_id, print_limit, messagebox):
    if not user_id or not print_limit.isdigit():
        messagebox.warning(
            None, 
            "Aviso", 
            "Insira um nome de usuário e um limite válido."
        )
        return

    try:
        with engine.connect() as connection:
            update_query = "UPDATE user_print_totals SET PrintLimit = :print_limit WHERE user = :user_id"
            rows_updated = connection.execute(
                text(update_query), 
                {'user_id': user_id, 'print_limit': int(print_limit)}
            ).rowcount

            if rows_updated == 0:
                messagebox.warning(
                    None, 
                    "Aviso", 
                    f"Nenhum usuário encontrado com o nome '{user_id}'."
                )
            else:
                # `commit` não é necessário no SQLAlchemy se estiver usando `engine.connect()`
                messagebox.information(
                    None, 
                    "Sucesso", 
                    f"Limite de impressão para '{user_id}' definido como {print_limit}!"
                )
    except Exception as e:
        messagebox.critical(
            None, 
            "Erro", 
            f"Erro ao definir o limite para o usuário '{user_id}': {e}"
        )
