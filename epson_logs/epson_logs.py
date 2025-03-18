import csv
import time
from playwright.sync_api import sync_playwright


def collect_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        # Epson IP 2.199
        page.goto("http://192.168.2.199")

        page.get_by_text("Início de sessão de administrador").click()
        page.locator("input[type='password']").fill("admin")
        page.get_by_text("OK").click()

        page.select_option("select", label="Configurações Avançadas")

        page.wait_for_selector('frame[name="MENU"]')
        menu_frame = page.frame(name="MENU")
        menu_frame.wait_for_selector("text='Estado de utilização'", state="visible")
        menu_frame.click("text='Estado de utilização'")

        frame = page.frame(name="CONTENTS")

        frame.evaluate("window.scrollBy(0, 500)")

        frame.wait_for_selector("dd.value.clearfix")

        # Cópias preto e branco
        try:
            copia_pb_locator = frame.locator(
                '//dt/span[contains(text(), "Cópia a P&B")]/ancestor::dt/following-sibling::dd//div[@class="preserve-white-space"]'
            )
            copia_pb = copia_pb_locator.first.text_content().strip()
        except Exception as e:
            copia_pb = f"Erro ao localizar: {e}"

        # Cópias coloridas
        try:
            copia_cor_locator = frame.locator(
                '//dt/span[contains(text(), "Cópia a Cor")]/ancestor::dt/following-sibling::dd//div[@class="preserve-white-space"]'
            )
            copia_cor = copia_cor_locator.first.text_content().strip()
        except Exception as e:
            copia_cor = f"Erro ao localizar: {e}"

        # Escrita CSV
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        printer_name = "Epson 2.199"
        with open("epson_logs/logs_epson.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Data", "Nome", "Cópia a P&B", "Cópia a Cor"])
            writer.writerow([current_time, printer_name, copia_pb, copia_cor])

        # Epson IP 2.210
        page.goto("http://192.168.2.210")

        page.get_by_text("Início de sessão de administrador").click()
        page.locator("input[type='password']").fill("admin")
        page.get_by_text("OK").click()

        page.select_option("select", label="Configurações Avançadas")

        page.wait_for_selector('frame[name="MENU"]')
        menu_frame = page.frame(name="MENU")
        menu_frame.wait_for_selector("text='Estado de utilização'", state="visible")
        menu_frame.click("text='Estado de utilização'")

        frame = page.frame(name="CONTENTS")

        frame.evaluate("window.scrollBy(0, 500)")

        frame.wait_for_selector("dd.value.clearfix")

        # Cópias preto e branco
        try:
            copia_pb_locator = frame.locator(
                '//dt/span[contains(text(), "Cópia a P&B")]/ancestor::dt/following-sibling::dd//div[@class="preserve-white-space"]'
            )
            copia_pb = copia_pb_locator.first.text_content().strip()
        except Exception as e:
            copia_pb = f"Erro ao localizar: {e}"

        # Cópias coloridas
        try:
            copia_cor_locator = frame.locator(
                '//dt/span[contains(text(), "Cópia a Cor")]/ancestor::dt/following-sibling::dd//div[@class="preserve-white-space"]'
            )
            copia_cor = copia_cor_locator.first.text_content().strip()
        except Exception as e:
            copia_cor = f"Erro ao localizar: {e}"

        # Escrita CSV
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        printer_name = "Epson 2.210"
        with open("epson_logs/logs_epson.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Data", "Nome", "Cópia a P&B", "Cópia a Cor"])
            writer.writerow([current_time, printer_name, copia_pb, copia_cor])

        input()

        # Fechar o navegador
        browser.close()


collect_data()
