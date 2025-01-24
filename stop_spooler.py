import time
import subprocess
from notification import show_notification
from popup import Popup


# Para o serviço de spooler e verifica o
def stop_spooler_service_if_needed(user, logged_in_user):
    """
    Interrompe o serviço do Spooler de Impressão se o usuário
    que atingiu o limite for o mesmo que está logado.
    """

    print(
        f"Usuário logado: {logged_in_user}\nUsuário que atingiu o limite de impressões {user}"
    )

    if logged_in_user and logged_in_user.lower() == user.lower():
        try:
            print(
                f"Usuário {user} atingiu o limite de impressão e está logado. Interrompendo o Spooler..."
            )

            # Popup.mostrar("Limite de impressões atingido",
            #     f"O usuário {user} atingiu o limite de impressões e foi bloqueado.",)
            
            # Mostra a notificação do windows
            print("Chamando not")
            show_notification(
                "Limite de impressões atingido",
                f"O usuário {user} atingiu o limite de impressões e foi bloqueado.",
                duration=15,
            )
            time.sleep(5)

            subprocess.run(
                ["sc", "stop", "PCPrintLogger"], check=True, text=True, shell=True)
            
            subprocess.run(["sc", "stop", "spooler"], check=True, text=True, shell=True)
            print("Serviço do Spooler de Impressão interrompido com sucesso.")

        except subprocess.CalledProcessError as e:
            print(f"Erro ao tentar parar o Spooler de Impressão: {e}")
            print(
                "Certifique-se de que o script está sendo executado com permissões de administrador."
            )
    else:
        print(
            f"Usuário {user} atingiu o limite, mas não está logado. O Spooler continuará funcionando."
        )