import json
from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from . import pedro
from .models import Empresa, Funcionario


def resposta_gemini(texto):
    """Simula a resposta HTTP da API do Gemini."""
    corpo = json.dumps({"candidates": [{"content": {"parts": [{"text": texto}]}}]})
    resposta = mock.MagicMock()
    resposta.read.return_value = corpo.encode("utf-8")
    resposta.__enter__.return_value = resposta
    return resposta


@override_settings(GEMINI_API_KEY="chave-de-teste", GEMINI_MODEL="modelo-teste")
class PedroTests(TestCase):

    def setUp(self):
        cache.clear()
        self.dono = User.objects.create_user("dono@teste.com", password="senha12345", first_name="Ana")
        self.empresa = Empresa.objects.create(
            nome_empresa="Padaria Sol", cidade_estado="Recife - PE",
            segmento="padaria", esg_02_separacao_lixo=True,
        )
        self.empresa.donos.add(self.dono)

    def perguntar(self, mensagem):
        return self.client.post(
            reverse("pedro_perguntar"),
            data=json.dumps({"mensagem": mensagem}),
            content_type="application/json",
        )

    def test_chat_exige_login(self):
        resposta = self.client.get(reverse("pedro_chat"))
        self.assertRedirects(resposta, reverse("entrar") + "?next=" + reverse("pedro_chat"),
                             fetch_redirect_response=False)

    def test_perguntar_sem_login_retorna_401(self):
        self.assertEqual(self.perguntar("Oi").status_code, 401)

    @mock.patch("core.pedro.urllib.request.urlopen")
    def test_pergunta_e_resposta_ficam_no_historico(self, urlopen):
        urlopen.return_value = resposta_gemini("Comece pelos **Pilares ESG**!")
        self.client.force_login(self.dono)

        resposta = self.perguntar("Por onde começo?")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["resposta"], "Comece pelos **Pilares ESG**!")

        # O contexto da empresa vai junto para o Gemini, e a chave vai no cabeçalho
        requisicao = urlopen.call_args[0][0]
        corpo = json.loads(requisicao.data)
        instrucoes = corpo["systemInstruction"]["parts"][0]["text"]
        self.assertIn("Padaria Sol", instrucoes)
        self.assertIn("realizadas: Separação Simples de Lixo", instrucoes)
        self.assertEqual(requisicao.get_header("X-goog-api-key"), "chave-de-teste")
        self.assertNotIn("chave-de-teste", requisicao.full_url)

        historico = self.client.session["pedro_historico"]
        self.assertEqual([m["autor"] for m in historico], ["usuario", "pedro"])

    @mock.patch("core.pedro.urllib.request.urlopen")
    def test_colaborador_tambem_conversa(self, urlopen):
        urlopen.return_value = resposta_gemini("Olá!")
        colaborador = User.objects.create_user("colab@teste.com", password="senha12345")
        Funcionario.objects.create(usuario=colaborador, empresa=self.empresa)
        self.client.force_login(colaborador)

        self.assertEqual(self.perguntar("Oi").status_code, 200)
        instrucoes = json.loads(urlopen.call_args[0][0].data)["systemInstruction"]["parts"][0]["text"]
        self.assertIn("colaborador(a)", instrucoes)

        self.assertContains(self.client.get(reverse("area_funcionario")), "Como posso ajudar hoje?")

    def test_pergunta_vazia_ou_longa(self):
        self.client.force_login(self.dono)
        self.assertEqual(self.perguntar("   ").status_code, 400)
        self.assertEqual(self.perguntar("a" * 1001).status_code, 400)

    @override_settings(GEMINI_API_KEY="")
    def test_sem_chave_mostra_mensagem_amigavel(self):
        self.client.force_login(self.dono)
        resposta = self.perguntar("Oi")
        self.assertEqual(resposta.status_code, 503)
        self.assertIn("GEMINI_API_KEY", resposta.json()["erro"])

    @mock.patch("core.pedro.urllib.request.urlopen")
    def test_limite_de_perguntas(self, urlopen):
        urlopen.return_value = resposta_gemini("Ok")
        self.client.force_login(self.dono)
        with mock.patch("core.views.PEDRO_LIMITE_PERGUNTAS", 2):
            self.assertEqual(self.perguntar("1").status_code, 200)
            self.assertEqual(self.perguntar("2").status_code, 200)
            self.assertEqual(self.perguntar("3").status_code, 429)

    @mock.patch("core.pedro.urllib.request.urlopen")
    def test_timeout_vira_mensagem_amigavel(self, urlopen):
        import socket
        urlopen.side_effect = socket.timeout("The read operation timed out")
        self.client.force_login(self.dono)
        resposta = self.perguntar("Oi")
        self.assertEqual(resposta.status_code, 503)
        self.assertIn("sem conexão", resposta.json()["erro"])

    def test_limpar_conversa(self):
        self.client.force_login(self.dono)
        sessao = self.client.session
        sessao["pedro_historico"] = [{"autor": "usuario", "texto": "Oi", "hora": ""}]
        sessao.save()
        self.client.post(reverse("pedro_limpar"))
        self.assertNotIn("pedro_historico", self.client.session)

    def test_card_no_inicio_e_login_volta_para_o_chat(self):
        self.assertContains(self.client.get(reverse("landing")), reverse("pedro_chat"))
        resposta = self.client.post(
            reverse("entrar") + "?next=" + reverse("pedro_chat"),
            {"username": "dono@teste.com", "password": "senha12345", "next": reverse("pedro_chat")},
        )
        self.assertRedirects(resposta, reverse("pedro_chat"), fetch_redirect_response=False)
        self.client.force_login(self.dono)
        self.assertContains(self.client.get(reverse("home")), "Como posso ajudar hoje?")
