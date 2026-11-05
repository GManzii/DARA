from playwright.sync_api import expect

def test_landing_page_loads(page):
    response = page.goto("http://127.0.0.1:8000/")

    assert response is not None
    assert response.status == 200

def test_landing_cadastro(page):
    # Open the landing page
    page.goto("http://127.0.0.1:8000/")

    # Click the registration button in the header
    page.locator("header a.btn-cadastro").click()

    # Verify navigation to the welcome page
    expect(page).to_have_url(
        "http://127.0.0.1:8000/inicio/"
    )

    # Verify the profile selection interface is available
    expect(
        page.locator('button[name="perfil"][value="dono"]')
    ).to_be_visible()

    expect(
        page.locator('button[name="perfil"][value="funcionario"]')
    ).to_be_visible()

def test_landing_entrar(page):
    # Open the landing page
    page.goto("http://127.0.0.1:8000/")

    # Click the login button in the header
    page.locator("header a.btn-entrar").click()

    # Verify navigation to the login page
    expect(page).to_have_url(
        "http://127.0.0.1:8000/entrar/"
    )

    # Verify the login form is present
    expect(page.locator("form")).to_be_visible()

def test_landing_pilares(page):
    # Open the landing page
    page.goto("http://127.0.0.1:8000/")

    # Click ESG Pilares in the navigation menu
    page.locator("header nav a[href='/pilares/']").click()

    # Verify navigation to the ESG pillars page
    expect(page).to_have_url(
        "http://127.0.0.1:8000/pilares/"
    )
