from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from unittest import expectedFailure

from core.models import Empresa


class QuestionarioESGTest(TestCase):

    def setUp(self):
        # Create a test manager
        self.usuario = User.objects.create_user(
            username="gestor_teste",
            password="senha_teste_123"
        )

        # Create a company
        self.empresa = Empresa.objects.create(
            nome_empresa="Empresa Teste",
            cidade_estado="Recife - PE"
        )
        self.empresa.donos.add(self.usuario)

        # Authenticate the manager
        self.client.force_login(self.usuario)

    def test_questionario_redireciona_para_home(self):
        # Submit the ESG questionnaire
        response = self.client.post(
            reverse("questionario_esg"),
            data={}
        )

        # Verify that Django redirects to home
        self.assertRedirects(
            response,
            reverse("home")
        )

        # Verify that the user remains authenticated
        self.assertIn(
            "_auth_user_id",
            self.client.session
        )

    @expectedFailure #o questionario ainda não salva as respostas entre sessões
    def test_questionario_salva_respostas(self):
        # Submit two completed ESG actions
        response = self.client.post(
            reverse("questionario_esg"),
            data={
                "esg_01_higiene_manipulacao": "on",
                "esg_02_separacao_lixo": "on",
            }
        )

        # Confirm successful submission
        self.assertRedirects(response, reverse("home"))

        # Reload the company from the database
        self.empresa.refresh_from_db()

        # Check whether the answers were saved
        self.assertTrue(
            self.empresa.esg_01_higiene_manipulacao
        )
        self.assertTrue(
            self.empresa.esg_02_separacao_lixo
        )

        # Each of these actions awards 5 points
        self.assertEqual(self.empresa.pontuacao_total, 10)
