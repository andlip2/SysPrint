import os
import shutil
import time
import subprocess
from datetime import datetime

# Caminho do arquivo original e da pasta de destino
arquivo_original = r"C:\Program Files (x86)\PaperCut Print Logger\logs\csv\papercut-print-log-all-time.csv"
pasta_destino = r"C:\Program Files (x86)\PaperCut Print Logger\logs\csv\backup"

# Obtém a data atual no formato YYYY-MM-DD
data_atual = datetime.now().strftime("%Y-%m-%d")

# Cria o novo nome do arquivo com base na data atual
novo_nome_arquivo = f"papercut-print-log-all-time-{data_atual}.csv"

# Caminho completo do arquivo de destino
destino_arquivo = os.path.join(pasta_destino, novo_nome_arquivo)

# Função para parar o serviço
def parar_servico(servico):
    try:
        subprocess.run(["sc", "stop", servico], check=True)
        print(f"Serviço {servico} parado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao parar o serviço {servico}: {e}")

# Função para iniciar o serviço
def iniciar_servico(servico):
    try:
        subprocess.run(["sc", "start", servico], check=True)
        print(f"Serviço {servico} iniciado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao iniciar o serviço {servico}: {e}")

# Função para mover o arquivo com tentativas
def mover_arquivo(arquivo_original, destino_arquivo, tentativas=5, intervalo=2):
    for _ in range(tentativas):
        try:
            shutil.move(arquivo_original, destino_arquivo)
            print(f"Arquivo movido e renomeado para: {destino_arquivo}")
            return True
        except PermissionError as e:
            print(f"Erro ao mover o arquivo: {e}. Tentando novamente...")
            time.sleep(intervalo)  # Aguarda antes de tentar novamente
    print("Não foi possível mover o arquivo após várias tentativas.")
    return False

# Função para garantir que a pasta de destino exista
def garantir_pasta_backup():
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"Pasta de backup criada: {pasta_destino}")
    else:
        print(f"Pasta de backup já existe: {pasta_destino}")

# Função principal que executa as etapas
def mover_arquivo_com_servico():
    servico = "PCPrintLogger"  # Nome do serviço

    # Para o serviço
    parar_servico(servico)

    # Garante que a pasta de backup exista
    garantir_pasta_backup()

    # Tenta mover o arquivo
    if mover_arquivo(arquivo_original, destino_arquivo):
        # Inicia o serviço novamente
        iniciar_servico(servico)

# Chama a função principal
mover_arquivo_com_servico()
