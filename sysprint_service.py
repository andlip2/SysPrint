import sys
import os
import win32serviceutil
import win32service
import win32event
import servicemanager
import time

class SysPrintService(win32serviceutil.ServiceFramework):
    _svc_name_ = "sysprints"
    _svc_display_name_ = "SysPrint Service"
    _svc_description_ = "Monitoramento de impressão do SysPrint."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        import main  # Chama o código principal
        main()  # Executa o código principal

def install_service():
    """Função para registrar o serviço."""
    try:
        # Verifica se o serviço já está instalado
        win32serviceutil.GetServiceStatus("sysprints")
        print("Serviço já está instalado.")
    except:
        # Caso não esteja instalado, instala o serviço
        win32serviceutil.InstallService(
            sys.executable,  # Caminho para o EXE
            "sysprints",      # Nome do serviço
            "SysPrint Service",  # Nome exibido
            startType=win32service.SERVICE_AUTO_START  # Tipo de inicialização
        )
        print("Serviço instalado com sucesso!")

def run_service():
    """Executa o serviço como um script normal."""
    print("Executando código normal")
    import main  # Chama o código principal
    main()  # Executa o código principal

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install_service()  # Instala o serviço se o argumento for "install"
    else:
        run_service()  # Caso contrário, executa o código normalmente
