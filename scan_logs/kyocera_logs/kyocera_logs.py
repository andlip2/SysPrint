import os
import csv
import glob
import datetime
import mysql.connector
from playwright.sync_api import sync_playwright


def collect_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)

        download_path = (
            "C:/Users/ana.beatriz/Documents/Ana/Projetos/"
            "SysPrint/scan_logs/kyocera_logs"
        )

        # Criar um contexto do navegador com suporte a downloads
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        page.goto("https://localhost:9292/")

        page.get_by_text("Relatórios", exact=True).click()

        page.locator("div.ui-grid-cell-contents span.ng-binding", has_text="Data").nth(
            1
        ).click()
        page.locator("div.ui-grid-cell-contents span.ng-binding", has_text="Data").nth(
            1
        ).click()

        page.locator(
            "div.ui-grid-cell-contents.ng-binding.ng-scope", has_text="scans_kyocera"
        ).nth(1).click()

        with page.expect_download() as download_info:
            page.locator(
                "div.row.ndm-toolbar-text.ndm-no-highlight.ng-binding",
                has_text="Fazer o Download",
            ).click()

        download = download_info.value
        download.save_as(f"{download_path}/{download.suggested_filename}")

        browser.close()


def add_date():
    download_path = (
        "C:/Users/ana.beatriz/Documents/Ana/Projetos/SysPrint/scan_logs/kyocera_logs"
    )
    csv_files = glob.glob(f"{download_path}/*.csv")
    latest_file = max(csv_files, key=os.path.getctime)

    output_file = latest_file.replace(".csv", "_edited.csv")

    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(latest_file, "r", encoding="utf-8-sig") as infile, open(
        output_file, "w", encoding="utf-8-sig", newline=""
    ) as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        headers = next(reader)
        headers.insert(0, "Data")  # Posição 0 para que a data seja o primeiro elemento
        writer.writerow(headers)

        for row in reader:
            row.insert(0, current_date)
            writer.writerow(row)


def db_upload(data):
    """Conexão com o banco"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sysprintdb",
            database="sysprint",
        )
        cursor = conn.cursor()

        serial_num = data[3]  # Número de série é o 4º item na lista (index 3)

        # Verifica se já existe um registro com o mesmo serial_num
        cursor.execute(
            "SELECT id_log FROM logs_scans WHERE serial_num = %s", serial_num
        )
        existing_record = cursor.fetchone()

        print(f"Verificando existência de {serial_num}: {existing_record}")

        if existing_record:
            # Se já existe, fazemos um UPDATE
            cursor.execute(
                """
                UPDATE logs_scans
                SET time = %s, printer_name = %s, ip = %s, 
                    bw_copies = %s
                WHERE serial_num = %s
                """,
                (data[0], data[1], data[2], data[4], serial_num),
            )
            print(f"Atualizando {serial_num}")
        else:
            # Se não existe, fazemos um INSERT
            cursor.execute(
                """
                INSERT INTO logs_scans (time, printer_name, ip, serial_num, bw_copies)
                VALUES (%s, %s, %s, %s, %s)
                """,
                data,
            )
            print(f"Inserindo {serial_num}")

        conn.commit()  # Garantir que as mudanças sejam persistidas no banco
    except mysql.connector.Error as e:
        print(f"Erro ao inserir no banco de dados: {e}")
    finally:
        conn.close()


def read_csv():
    """Lê o CSV e adiciona os dados ao banco"""
    download_path = (
        "C:/Users/ana.beatriz/Documents/Ana/Projetos/SysPrint/scan_logs/kyocera_logs"
    )
    csv_files = glob.glob(f"{download_path}/*.csv")
    latest_file = max(csv_files, key=os.path.getctime)

    with open(latest_file, mode="r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader)  # Pula o cabeçalho

        for row in reader:
            try:
                bw_copies = int(row[4])
            except ValueError:
                bw_copies = 0

            data = (
                row[0],
                row[3],
                row[1],
                row[2],
                bw_copies,
            )
            db_upload(data)


collect_data()
add_date()
read_csv()
