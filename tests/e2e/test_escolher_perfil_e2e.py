from playwright.sync_api import expect


def test_escolher_gerente(page):
    # Open the welcome page
    page.goto("http://127.0.0.1:8000/inicio/")

    # Find the manager selection button
    botao_gerente = page.locator(
        'button[name="perfil"][value="dono"]'
    )

    # Verify the button is visible
    expect(botao_gerente).to_be_visible()

    # Click the manager option
    botao_gerente.click()

    # Verify the browser reached manager registration
    expect(page).to_have_url(
        "http://127.0.0.1:8000/dono/"
    )


def test_escolher_funcionario(page):
    # Open the welcome page
    page.goto("http://127.0.0.1:8000/inicio/")

    # Find the employee selection button
    botao_funcionario = page.locator(
        'button[name="perfil"][value="funcionario"]'
    )

    # Verify the button is visible
    expect(botao_funcionario).to_be_visible()

    # Click the employee option
    botao_funcionario.click()

    # Verify the browser reached employee registration
    expect(page).to_have_url(
        "http://127.0.0.1:8000/cadastro-funcionario/"
    )

