from playwright.sync_api import sync_playwright


def collect_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        # Link para a página web
        page.goto("http://192.168.2.199")

        page.get_by_text("Início de sessão de administrador").click()
        page.locator("input[type='password']").fill("admin")
        page.get_by_text("OK").click()

        page.select_option("select", label="Configurações Avançadas")

        page.wait_for_selector('frame[name="MENU"]')
        menu_frame = page.frame(name="MENU")
        menu_frame.wait_for_selector("text='Estado de utilização'", state="visible")
        menu_frame.click("text='Estado de utilização'")

        frame = page.frame(name="CONTENTS")  # Acessa o frame "CONTENTS"

        # Rolagem para garantir que o conteúdo esteja visível
        frame.evaluate("window.scrollBy(0, 500)")  # Rola 500px para baixo

        # Esperar pelos elementos de "Cópia a P&B" e "Cópia a Cor" ficarem visíveis
        frame.wait_for_selector(
            "dd.value.clearfix"
        )  # Espera o dd que contém os valores

        # Localizar o valor de "Cópia a P&B"
        try:
            copia_pb_locator = frame.locator(
                '//dt/span[contains(text(), "Cópia a P&B")]/ancestor::dt/following-sibling::dd//div[@class="preserve-white-space"]'
            )
            copia_pb = copia_pb_locator.first.text_content().strip()
        except Exception as e:
            copia_pb = f"Erro ao localizar: {e}"

        # Localizar o valor de "Cópia a Cor"
        try:
            copia_cor_locator = frame.locator(
                '//dt/span[contains(text(), "Cópia a Cor")]/ancestor::dt/following-sibling::dd//div[@class="preserve-white-space"]'
            )
            copia_cor = copia_cor_locator.first.text_content().strip()
        except Exception as e:
            copia_cor = f"Erro ao localizar: {e}"

        # Exibir os valores no console
        print(f"Cópia a P&B: {copia_pb}")
        print(f"Cópia a Cor: {copia_cor}")

        # Salvar os valores em um arquivo
        with open("epson_logs/logs_epson.txt", "a") as file:
            file.write(f"Cópia a P&B: {copia_pb}\n")
            file.write(f"Cópia a Cor: {copia_cor}\n")

        print("Valores salvos em logs_epson.txt")

        # Fechar o navegador
        browser.close()


collect_data()
