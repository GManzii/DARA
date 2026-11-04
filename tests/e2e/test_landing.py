def test_landing_page_loads(page):
    response = page.goto("http://127.0.0.1:8000/")

    assert response is not None
    assert response.status == 200