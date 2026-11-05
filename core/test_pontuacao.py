from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from playwright.sync_api import sync_playwright, expect

from core.models import Empresa


class PontuacaoE2ETest(LiveServerTestCase):

    def setUp(self):
        # Create a manager in the temporary test database
        self.usuario = User.objects.create_user(
            username="gestor_teste",
            password="senha_teste_123"
        )

        # Create a company
        self.empresa = Empresa.objects.create(
            nome_empresa="Empresa Teste",
            cidade_estado="Recife - PE"
        )

        # Associate the manager with the company
        self.empresa.donos.add(self.usuario)

    def test_pontuacao_inicial(self):
        # No ESG actions have been completed
        self.assertEqual(self.empresa.pontuacao_total, 0)

    def test_pontuacao_apos_acao(self):
        # Complete one low-priority action
        self.empresa.esg_01_higiene_manipulacao = True
        self.empresa.save()

        # Verify the calculated score
        self.assertEqual(self.empresa.pontuacao_total, 5)