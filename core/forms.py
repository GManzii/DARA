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