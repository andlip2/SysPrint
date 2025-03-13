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

        # Alterar para uma lógica que procure pela string na tela
        """ first_value = (
            page.locator("dd.value.clearfix div.preserve-white-space")
            .nth(0)
            .text_content()
        )
        second_value = (
            page.locator("dd.value.clearfix div.preserve-white-space")
            .nth(1)
            .text_content()
        )

        print(f"Primeiro valor: {first_value}\nSegundo valor: {second_value}")

        with open("estado_utilizacao.txt", "w") as file:
            file.write(f"Primeiro valor: {first_value}\n")
            file.write(f"Segundo valor: {second_value}\n") """

        print("Teste concluído.")
        input()

        browser.close()


collect_data()
