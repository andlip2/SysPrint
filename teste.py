import wmi

def get_active_user_wmi():
    try:
        c = wmi.WMI()
        for session in c.Win32_ComputerSystem():
            username = session.UserName
            if username:
                # Divide a string pelo caractere '\' e pega apenas o nome de usuário
                user = username.split("\\")[-1]
                print(f"Usuário ativo atualmente: {user}")
                return user
        return None
    except Exception as e:
        print(f"Erro ao obter o usuário ativo: {e}")
        return None

if __name__ == "__main__":
    get_active_user_wmi()
