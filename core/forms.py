from django import forms
from .models import Empresa, MensagemContato
from django.contrib.auth.models import User

# 1. Formulário para Fale Conosco 
class ContatoForm(forms.ModelForm):
    class Meta:
        model = MensagemContato
        fields = ['nome', 'email', 'tipo', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Seu e-mail'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escreva sua mensagem...'}),
        }
# 2. Cadastro do dono
class UsuarioDonoForm(forms.ModelForm):
    nome_completo = forms.CharField(
        max_length=150,
        label="Nome Completo",
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome completo'})
    )
    telefone = forms.CharField(
        max_length=20,
        label="Telefone",
        widget=forms.TextInput(attrs={'placeholder': '(xx) xxxxx-xxxx'})
    )
    senha = forms.CharField(
        label="Definir Senha",
        widget=forms.PasswordInput(attrs={'placeholder': 'Sua senha'})
    )
    confirmar_senha = forms.CharField(
        label="Confirmar Senha",
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita sua senha'})
    )

    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'seuemail@exemplo.com'}),
        }

    # Validação para garantir que as senhas são iguais
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if senha and confirmar_senha and senha != confirmar_senha:
            raise forms.ValidationError("As senhas não coincidem.")
        return cleaned_data

# 3. Questionário do cadastro da empresa (dono)
class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            'nome_empresa',
            'segmento',
            'porte',
            'numero_funcionarios',
            'cidade_estado'
        ]

# 4. Form do Questionário ESG 
class QuestionarioESGForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            'esg_01_higiene_manipulacao',
            'esg_02_separacao_lixo',
            'esg_03_coleta_oleo',
            'esg_04_combate_desperdicio',
            'esg_05_cardapio_transparente',
            'esg_06_recibos_digitais',
            'esg_07_aeradores_torneiras',
            'esg_08_organizacao_pvps',
            'esg_09_descarte_lampadas_baterias',
            'esg_10_caixa_sugestoes',
            'esg_11_apagando_luz',
            'esg_12_uso_consciente_embalagens',
            'esg_13_doacao_excedente',
            'esg_14_troca_descartaveis',
            'esg_15_apoio_anti_lesao',
            'esg_16_compra_produtor_local',
            'esg_17_planilha_perdas',
            'esg_18_compostagem_basica',
            'esg_19_folga_aniversario_bem_estar',
            'esg_20_treinamento_diversidade',
            'esg_21_ovos_cage_free_compra_etica',
            'esg_22_equipamentos_inverter',
            'esg_23_opcoes_plant_based',
            'esg_24_selo_certificacao_local',
            'esg_25_energia_solar',
        ]

class UsuarioDonoForm(forms.ModelForm):
    nome_completo = forms.CharField(
        max_length=150,
        label="Nome Completo",
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome completo'})
    )
    telefone = forms.CharField(
        max_length=20,
        label="Telefone",
        widget=forms.TextInput(attrs={'placeholder': '(xx) xxxxx-xxxx'})
    )
    senha = forms.CharField(
        label="Definir Senha",
        widget=forms.PasswordInput(attrs={'placeholder': 'Sua senha'})
    )
    confirmar_senha = forms.CharField(
        label="Confirmar Senha",
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita sua senha'})
    )

    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'seuemail@exemplo.com'}),
        }

    # Validação para impedir e-mails duplicados
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado no sistema.")
        return email

    # Validação das senhas
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if senha and confirmar_senha and senha != confirmar_senha:
            raise forms.ValidationError("As senhas não coincidem.")
        return cleaned_data