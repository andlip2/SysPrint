import csv
import time
import mysql.connector
from playwright.sync_api import sync_playwright


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

        """ Inserção na tabela 'logs_scans' """
        cursor.execute(
            """
        INSERT INTO logs_scans (time, printer_name, ip, serial_num, bw_copies, colorful_copies)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
            data,
        )

        conn.commit()
    except mysql.connector.Error as e:
        print(f"Erro ao inserir no banco de dados: {e}")
    finally:
        conn.close()


def read_csv():
    """Lê o CSV e adiciona os dados ao banco"""
    with open("epson_logs/logs_epson.csv", mode="r", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            db_upload(row)


def csv_generator(data):
    """Recebe os dados copiados das interfaces e os parâmetros passados na lista 'printers'"""
    with open(
        "epson_logs/logs_epson.csv", mode="a", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)
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


""" Chama as funções """
collect_data()


read_csv()
