from playwright.sync_api import sync_playwright


def collect_data():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)

        download_path = "C:/Users/ana.beatriz/Downloads"

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

        """ div no html:
        <div class="row ndm-toolbar-text ndm-no-highlight ng-binding">Fazer o Download</div>
        Para usá-la no page.locator, troque os espaços por pontos. """

        input()

        # Fechar o navegador
        # browser.close()


collect_data()
