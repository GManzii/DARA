
from playwright.sync_api import expect


def test_pilares_navigation(page):
    page.goto("http://127.0.0.1:8000/pilares/")

    # The Ambiental tab is selected by default
    ambiental = page.get_by_role("tab", name="Ambiental")
    social = page.get_by_role("tab", name="Social")
    governanca = page.get_by_role("tab", name="Governança")

    expect(ambiental).to_have_attribute("aria-selected", "true")

    # Switch to Social
    social.click()
    expect(social).to_have_attribute("aria-selected", "true")
    expect(page.locator("#painel-social")).to_be_visible()

    # Switch to Governança
    governanca.click()
    expect(governanca).to_have_attribute("aria-selected", "true")
    expect(page.locator("#painel-governanca")).to_be_visible()

    # Switch back to Ambiental
    ambiental.click()
    expect(page.locator("#painel-ambiental")).to_be_visible()


def test_visitante_nao_pode_editar_checklist(page):
    page.goto("http://127.0.0.1:8000/pilares/")

    checkboxes = page.locator(
        '#form-ambiental input[type="checkbox"]'
    )

    assert checkboxes.count() > 0

    for checkbox in checkboxes.all():
        expect(checkbox).to_be_disabled()
