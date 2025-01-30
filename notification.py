import sys
import time
import threading
from win10toast import ToastNotifier
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw


# Notificação do Windows
def show_notification(title, message, duration):
    try:
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=duration, threaded=True)
    except Exception as e:
        print(f"Erro ao mostrar a notificação: {e}")


# Ícone na bandeja do sistema
def create_tray_icon():
    # Cria a imagem do ícone
    image = Image.new("RGBA", (64, 64), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 64, 64), fill="blue")  # Adiciona o fundo da imagem

    # Menu para o ícone da bandeja
    menu = Menu(
        MenuItem("Mostrar notificação", show_notification_action),
        MenuItem("Sair", exit_action),
    )

    # Cria o ícone e executa na bandeja
    icon = Icon("SysPrint", image, menu=menu)
    icon.run()


# Ação do menu para mostrar a notificação
def show_notification_action(icon, item):
    show_notification("SysPrint", "Notificação do SysPrint!", duration=10)


# Ação do menu para sair
def exit_action(icon, item):
    icon.stop()


# Executa o tray app como um processo separado
def start_tray_app():
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()


# Função principal para rodar a aplicação
def run():
    # Inicia o tray app em segundo plano
    start_tray_app()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    run()
