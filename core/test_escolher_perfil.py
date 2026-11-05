from django.test import TestCase
from django.urls import reverse


class EscolherPerfilTest(TestCase):

    def test_escolher_dono(self):
        # Simulate choosing the business-owner profile
        response = self.client.post(
            reverse("escolher_perfil"),
            data={"perfil": "dono"}
        )

        # Verify the user is sent to owner registration
        self.assertRedirects(
            response,
            reverse("area_dono"),
            fetch_redirect_response=False
        )

        # Verify the selected profile was saved in the session
        self.assertEqual(
            self.client.session.get("perfil"),
            "dono"
        )
    
    def test_escolher_funcionario(self):
        # Simulate choosing the employee profile
        response = self.client.post(
            reverse("escolher_perfil"),
            data={"perfil": "funcionario"}
        )

        # Verify the redirect to employee registration
        self.assertRedirects(
            response,
            reverse("cadastro_funcionario"),
            fetch_redirect_response=False
        )
    
    def test_escolher_perfil_invalido(self):
        # Submit a profile that doesn't exist
        response = self.client.post(
            reverse("escolher_perfil"),
            data={"perfil": "administrador"}
        )

        # Verify that the user is redirected to home
        self.assertRedirects(
            response,
            reverse("home"),
            fetch_redirect_response=False
        )

        # Verify that no valid profile was selected
        self.assertNotIn(
            "perfil",
            self.client.session
        )

    def test_escolher_funcionario_salva_sessao(self):
        response = self.client.post(
            reverse("escolher_perfil"),
            data={"perfil": "funcionario"}
        )

        self.assertRedirects(
            response,
            reverse("cadastro_funcionario"),
            fetch_redirect_response=False
        )

        self.assertEqual(
            self.client.session.get("perfil"),
            "funcionario"
        )
