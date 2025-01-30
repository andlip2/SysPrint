import time
import threading
from sqlalchemy import create_engine, text
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
from plyer import notification
import wmi
import pythoncom

# Configurações do banco de dados
db_url = "mysql+pymysql://admin_user:admsysp%4025@192.168.1.226:3306/sysprint"
engine = create_engine(db_url)


def get_logged_in_user():
    """Obtém o nome do usuário atualmente logado no sistema."""
    try:
        pythoncom.CoInitialize()  # Inicializa o COM para a thread atual
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
    finally:
        pythoncom.CoUninitialize()  # Finaliza o COM para liberar recursos

def exibir_notificacao(titulo, mensagem):
    """Exibe uma notificação no sistema operacional."""
    notification.notify(
        title=titulo,
        message=mensagem,
        app_name="Monitor de Impressões",
        timeout=10  # Tempo em segundos para exibir a notificação
    )

# Variável para controle do monitoramento
monitorando = True

def criar_icone():
    """Desenha um ícone circular para o Tray App."""
    largura, altura = 64, 64
    imagem = Image.new("RGBA", (largura, altura), (255, 255, 255, 0))
    draw = ImageDraw.Draw(imagem)
    draw.ellipse((8, 8, largura - 8, altura - 8), fill="blue")
    return imagem

def verificar_limites():
    """Verifica os limites de impressão e notifica caso sejam ultrapassados."""
    global monitorando
    while monitorando:
        try:
            with engine.connect() as connection:
                # Consulta para somar Pages * Copies por usuário
                query_logs = """
                    SELECT 
                        `User`, 
                        SUM(`Pages` * `Copies`) AS total_impressao
                    FROM logs
                    GROUP BY `User`;
                """
                result_logs = connection.execute(text(query_logs))
                usuarios_logs = {row[0]: row[1] for row in result_logs}

                # Consulta para obter os limites de impressão e departamentos dos usuários
                query_users = """
                    SELECT 
                        `User`, 
                        `PrintLimit`, 
                        `Department`
                    FROM users;
                """
                result_users = connection.execute(text(query_users))
                usuarios_info = {row[0]: {"PrintLimit": row[1], "Department": row[2]} for row in result_users}

                # Consulta para obter os limites de impressão por departamento
                query_departments = """
                    SELECT 
                        `Department`, 
                        `TotalLimit`
                    FROM department_limits;
                """
                result_departments = connection.execute(text(query_departments))
                departamentos_limits = {row[0]: row[1] for row in result_departments}

                # Obtém o usuário atualmente logado
                usuario_logado = get_logged_in_user()

                # Verifica limites e notifica apenas para o usuário logado
                for user, total_impressao in usuarios_logs.items():
                    usuario_info = usuarios_info.get(user, {})
                    print_limit = usuario_info.get("PrintLimit", 0)
                    departamento = usuario_info.get("Department", None)

                    # Se o limite do usuário for 0, usa o limite do departamento
                    if print_limit == 0 and departamento in departamentos_limits:
                        print_limit = departamentos_limits[departamento]

                    if (
                        print_limit is not None 
                        and total_impressao >= print_limit
                        and user == usuario_logado  # Exibe apenas para o usuário logado
                    ):
                        mensagem = (
                            f"Usuário {user} atingiu o limite de impressão!\n"
                            f"Total: {total_impressao}, Limite: {print_limit}"
                        )
                        print(f"⚠️ {mensagem}")
                        exibir_notificacao("Limite de Impressão Atingido", mensagem)
        except Exception as e:
            print(f"Erro ao verificar limites: {e}")
        time.sleep(60)  # Aguarda 60 segundos antes de verificar novamente


def iniciar_monitoramento():
    """Inicia o monitoramento em uma thread separada."""
    global monitorando
    monitorando = True
    thread = threading.Thread(target=verificar_limites, daemon=True)
    thread.start()

def parar_monitoramento():
    """Para o monitoramento."""
    global monitorando
    monitorando = False
    print("Monitoramento pausado.")

def sair(icon):
    """Encerra o Tray App."""
    parar_monitoramento()
    icon.stop()

def criar_tray_app():
    """Cria o Tray App com um menu interativo."""
    menu = Menu(
        MenuItem("Iniciar Monitoramento", iniciar_monitoramento, default=True),
        MenuItem("Parar Monitoramento", parar_monitoramento),
        MenuItem("Sair", sair)
    )
    icone = Icon("Print Monitor", criar_icone(), "Monitor de Impressões", menu)
    return icone

if __name__ == "__main__":
    print("Iniciando Tray App...")
    iniciar_monitoramento()
    tray_app = criar_tray_app()
    tray_app.run()
