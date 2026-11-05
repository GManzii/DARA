from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from playwright.sync_api import sync_playwright, expect

from core.models import Empresa


class ChecklistE2ETest(LiveServerTestCase):

    def setUp(self):
        # Create a manager in the test database
        self.usuario = User.objects.create_user(
            username="gestor_teste",
            password="senha_teste_123"
        )

        # Create a company and associate the manager
        self.empresa = Empresa.objects.create(
            nome_empresa="Empresa Teste",
            cidade_estado="Recife - PE"
        )
        self.empresa.donos.add(self.usuario)

    def test_checklist_persiste_e_atualiza_pontuacao(self):

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            try:
                # Authenticate using Django's session mechanism
                from django.contrib.sessions.backends.db import SessionStore
                from django.contrib.auth import (
                    SESSION_KEY,
                    BACKEND_SESSION_KEY,
                    HASH_SESSION_KEY,
                )

                session = SessionStore()
                session[SESSION_KEY] = str(self.usuario.pk)
                session[BACKEND_SESSION_KEY] = (
                    "django.contrib.auth.backends.ModelBackend"
                )
                session[HASH_SESSION_KEY] = (
                    self.usuario.get_session_auth_hash()
                )
                session.save()

                # Add the session cookie to the browser
                context.add_cookies([{
                    "name": "sessionid",
                    "value": session.session_key,
                    "url": self.live_server_url,
                }])

                # Open ESG checklist
                page.goto(f"{self.live_server_url}/pilares/")

                # Select the first ESG action
                checkbox = page.locator(
                    'input[name="esg_01_higiene_manipulacao"]'
                )

                expect(checkbox).to_be_enabled()
                checkbox.check()

                # Submit the Ambiental checklist
                page.locator("#form-ambiental").evaluate(
                    "(form) => form.requestSubmit()"
                )

                # Wait for the save request to complete
                page.wait_for_load_state("networkidle")

                # Reload and verify persistence
                page.reload()

                checkbox = page.locator(
                    'input[name="esg_01_higiene_manipulacao"]'
                )
                expect(checkbox).to_be_checked()

                # Verify the score in the database
                self.empresa.refresh_from_db()
                self.assertEqual(self.empresa.pontuacao_total, 5)

            finally:
                browser.close()
