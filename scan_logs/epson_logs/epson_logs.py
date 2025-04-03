import os
import csv
import servicemanager
import time
import datetime
import mysql.connector
from playwright.sync_api import sync_playwright

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(
    os.path.dirname(__file__), "browsers"
)

# Gera um nome único para o CSV a cada execução usando um timestamp
CSV_FILENAME = os.path.join(
    "C:/Users/ana.beatriz/Documents/Ana/Projetos/SysPrint/scan_logs/epson_logs",
    "logs_epson_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv",
)


def db_upload(data):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="sysprintdb",
            database="sysprint",
        )
        cursor = conn.cursor()

        serial_num = data[3]  # Número de série é o 4º item na lista (index 3)

        # 🔍 Verifica se já existe um registro com o mesmo serial_num
        cursor.execute(
            "SELECT id_log FROM logs_scans WHERE serial_num = %s", (serial_num)
        )
        existing_record = cursor.fetchone()
        cursor.nextset()  # Garante que a consulta foi completamente processada

        print(
            f"Verificando existência de {serial_num}: {existing_record}"  # Verificação de retorno
        )

        if existing_record:
            # 🔄 Se já existe, fazemos um UPDATE, mas sem afetar o número de série
            cursor.execute(
                """
                UPDATE logs_scans
                SET time = %s, printer_name = %s, ip = %s, 
                    bw_copies = %s, colorful_copies = %s
                WHERE serial_num = %s
                """,
                (
                    data[0],
                    data[1],
                    data[2],
                    data[4],
                    data[5],
                    serial_num,
                ),  # Atualizando apenas os campos relevantes
            )
            print(f"Atualizando {serial_num}")
        else:
            # ➕ Se não existe, fazemos um INSERT
            cursor.execute(
                """
                INSERT INTO logs_scans (time, printer_name, ip, serial_num, bw_copies, colorful_copies)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                data,
            )
            print(f"Inserindo {serial_num}")

        conn.commit()  # Garantir que as mudanças sejam persistidas no banco
    except mysql.connector.Error as e:
        print(f"Erro ao inserir no banco de dados: {e}")
    finally:
        cursor.close()
        conn.close()


def read_csv():
    """Lê o CSV e adiciona os dados ao banco"""
    with open(CSV_FILENAME, mode="r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader)  # Pula o cabeçalho
        for row in reader:
            db_upload(row)  # Cada linha do CSV é processada


def csv_generator(data):
    """Recebe os dados copiados das interfaces e os parâmetros passados na lista 'printers'"""
    with open(CSV_FILENAME, mode="a", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        # Se o arquivo estiver vazio, escreve o cabeçalho
        if file.tell() == 0:
            writer.writerow(
                ["Data", "Nome", "IP", "Número de Série", "Cópia a P&B", "Cópia a Cor"]
            )
        writer.writerow(data)


def go_to_interface(page, ip, printer_name):
    """Navega pelas interfaces e copia os dados necessários"""
    page.goto(f"http://{ip}")
    page.get_by_text("Início de sessão de administrador").click()
    page.locator("input[type='password']").fill("admin")
    page.get_by_text("OK").click()
    page.select_option("select", label="Configurações Avançadas")

    frame = page.frame(name="CONTENTS")
    frame.evaluate("window.scrollBy(0, 500)")

    # Número de série
    try:
        serial_num_locator = frame.locator(
            '//dt/span[contains(text(), "Número de série")]/ancestor::dt/following-sibling::dd//div[@class="preserve-white-space"]'
        )
        serial_num = serial_num_locator.first.text_content().strip()
    except Exception as e:
        serial_num = f"Erro ao localizar: {e}"

    page.wait_for_selector('frame[name="MENU"]')
    menu_frame = page.frame(name="MENU")
    menu_frame.wait_for_selector("text='Estado de utilização'", state="visible")
    menu_frame.click("text='Estado de utilização'")

    frame = page.frame(name="CONTENTS")
    frame.evaluate("window.scrollBy(0, 500)")
    frame.wait_for_selector("dd.value.clearfix")

    # Cópias preto e branco
    try:
        bw_copies_locator = frame.locator(
            '//dt/span[contains(text(), "Cópia a P&B")]/ancestor::dt/following-sibling::dd//div[@class="preserve-white-space"]'
        )
        bw_copies = bw_copies_locator.first.text_content().strip()
    except Exception as e:
        bw_copies = f"Erro ao localizar: {e}"

    # Cópias coloridas
    try:
        colorful_copies_locator = frame.locator(
            '//dt/span[contains(text(), "Cópia a Cor")]/ancestor::dt/following-sibling::dd//div[@class="preserve-white-space"]'
        )
        colorful_copies = colorful_copies_locator.first.text_content().strip()
    except Exception as e:
        colorful_copies = f"Erro ao localizar: {e}"

    # Escrita CSV
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    data = [current_time, printer_name, ip, serial_num, bw_copies, colorful_copies]
    csv_generator(data)


def collect_data():
    """Configura a navegação e passa parâmetros dentro de 'printers'"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        printers = [
            ("192.168.2.199", "L6490 Series"),
            ("192.168.2.210", "L6490 Series"),
        ]

        for ip, printer_name in printers:
            go_to_interface(page, ip, printer_name)

        browser.close()


collect_data()
read_csv()
