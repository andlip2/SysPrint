@echo off

:: Definir variáveis de caminho
set SERVICE_NAME=sysprints
set SERVICE_DISPLAY_NAME=SysPrint Service
set SERVICE_PATH=C:\SysPrint\main.exe
set NSSM_PATH=C:\SysPrint\nssm.exe

:: Verifica se o nssm.exe existe
if not exist "%NSSM_PATH%" (
    echo O arquivo nssm.exe nao foi encontrado. Abortando.
    pause
    exit /b 1
)

:: Instalar o serviço usando o nssm
"%NSSM_PATH%" install "%SERVICE_NAME%" "%SERVICE_PATH%"

:: Definir o nome e a descrição do serviço
"%NSSM_PATH%" set "%SERVICE_NAME%" DisplayName "%SERVICE_DISPLAY_NAME%"
"%NSSM_PATH%" set "%SERVICE_NAME%" Description "Monitoramento de impressão do SysPrint."

:: Iniciar o serviço
"%NSSM_PATH%" start "%SERVICE_NAME%"

:: Confirmação
echo O serviço %SERVICE_NAME% foi instalado e iniciado com sucesso.

:: Fechar o terminal automaticamente
exit
