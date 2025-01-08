from sqlalchemy import create_engine, text

# Configurações do banco de dados
db_url = "mysql+pymysql://app_user:sysprintusertest@192.168.1.226:3306/sysprint"
engine = create_engine(db_url)

def set_user_limit(user_id, print_limit, messagebox):
    if not user_id or not print_limit.isdigit():
        messagebox.showwarning("Aviso", "Insira um nome de usuário e um limite válido.")
        return

    try:
        with engine.connect() as connection:
            update_query = "UPDATE user_print_totals SET PrintLimit = :print_limit WHERE user = :user_id"
            rows_updated = connection.execute(text(update_query), {'user_id': user_id, 'print_limit': int(print_limit)}).rowcount

            if rows_updated == 0:
                messagebox.showwarning("Aviso", f"Nenhum usuário encontrado com o nome '{user_id}'.")
            else:
                connection.commit()
                messagebox.showinfo("Sucesso", f"Limite de impressão para '{user_id}' definido como {print_limit}!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao definir o limite para o usuário '{user_id}': {e}")
