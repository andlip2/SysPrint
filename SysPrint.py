import os
import time
import csv
from datetime import datetime
from sqlalchemy import create_engine, text
import win32serviceutil
import win32service
import win32api
import win32con
import logging
import threading

class PaperCutService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'PaperCutService'
    _svc_display_name_ = 'PaperCut Log Monitoring Service'
    _svc_description_ = 'Monitora o arquivo de log do PaperCut e envia os dados para o banco de dados.'

    def __init__(self, args):
        super().__init__(args)
        self.db_url = "mysql+pymysql://root:@localhost:3306/teste_rc"  # Conexão corrigida, sem senha ou com a senha adequada
        self.db_engine = create_engine(self.db_url)
        self.log_file_path = r"C:\\Program Files (x86)\\PaperCut Print Logger\\logs\\csv\\papercut-print-log-all-time.csv"
        self.last_checked_time = datetime.now()

    def create_table(self):
        """Cria a tabela no banco de dados se ela não existir."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS logs (
            Time DATETIME,
            User VARCHAR(255),
            Pages INT,
            Copies INT,
            Printer VARCHAR(255),
            DocumentName VARCHAR(255),
            Client VARCHAR(255),
            PaperSize VARCHAR(50),
            Language VARCHAR(50),
            Height FLOAT,
            Width FLOAT,
            Duplex BOOLEAN,
            Grayscale BOOLEAN,
            Size FLOAT
        ) ENGINE=InnoDB;
        """
        try:
            with self.db_engine.connect() as connection:
                connection.execute(text(create_table_query))
                print("Tabela criada ou já existente.")
        except Exception as e:
            print(f"Erro ao criar a tabela: {e}")

    def read_and_store_logs(self):
        """Lê o arquivo CSV de log e armazena os dados no banco de dados."""
        try:
            with open(self.log_file_path, 'r', newline='', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Pula o cabeçalho
                next(csv_reader)  # Pula a segunda linha, conforme solicitado
                for row in csv_reader:
                    if len(row) >= 12:  # Verifica se há dados suficientes na linha
                        time_str = row[0]
                        user = row[1]
                        pages = int(row[2]) if row[2].isdigit() else 0
                        copies = int(row[3]) if row[3].isdigit() else 0
                        printer = row[4]
                        document_name = row[5]
                        client = row[6]
                        paper_size = row[7]
                        language = row[8]
                        height = float(row[9]) if row[9].replace('.', '', 1).isdigit() else 0
                        width = float(row[10]) if row[10].replace('.', '', 1).isdigit() else 0
                        duplex = True if row[11].lower() == 'true' else False
                        grayscale = True if row[10].lower() == 'true' else False
                        size = float(row[11]) if row[11].replace('.', '', 1).isdigit() else 0

                        # Converter o tempo para formato de data/hora
                        log_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

                        insert_query = """
                        INSERT INTO logs (Time, User, Pages, Copies, Printer, DocumentName, Client, PaperSize, Language, Height, Width, Duplex, Grayscale, Size)
                        VALUES (:Time, :User, :Pages, :Copies, :Printer, :DocumentName, :Client, :PaperSize, :Language, :Height, :Width, :Duplex, :Grayscale, :Size)
                        """
                        with self.db_engine.connect() as connection:
                            connection.execute(text(insert_query), {
                                'Time': log_time,
                                'User': user,
                                'Pages': pages,
                                'Copies': copies,
                                'Printer': printer,
                                'DocumentName': document_name,
                                'Client': client,
                                'PaperSize': paper_size,
                                'Language': language,
                                'Height': height,
                                'Width': width,
                                'Duplex': duplex,
                                'Grayscale': grayscale,
                                'Size': size
                            })
                            print(f"Log {log_time} armazenado com sucesso.")
        except Exception as e:
            print(f"Erro ao ler o arquivo de log ou armazenar os dados: {e}")

    def monitor_logs(self):
        """Monitora o arquivo de log continuamente e envia os dados para o banco de dados."""
        self.create_table()  # Cria a tabela no banco de dados se necessário
        while True:
            current_time = datetime.now()
            # Verificar se passou tempo suficiente para processar os novos logs
            if (current_time - self.last_checked_time).seconds >= 60:  # Processa a cada minuto
                self.read_and_store_logs()
                self.last_checked_time = current_time
            time.sleep(10)

    def SvcStop(self):
        """Para o serviço."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        print("Serviço de monitoramento parado.")
        self.Stop()

    def SvcDoRun(self):
        """Inicia o serviço."""
        print("Serviço de monitoramento iniciado.")
        log_thread = threading.Thread(target=self.monitor_logs)
        log_thread.daemon = True
        log_thread.start()
        self.wait_for_service_to_stop()

    def wait_for_service_to_stop(self):
        """Aguarda o serviço ser parado."""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Serviço interrompido manualmente.")
            self.SvcStop()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PaperCutService)
