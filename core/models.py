from django.db import models
from django.contrib.auth.models import User


class MensagemContato(models.Model):
    TIPO_CHOICES = [
        ('bug', 'Bug / Erro'),
        ('sugestao', 'Sugestão'),
        ('outros', 'Outros'),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail")
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        default='sugestao', 
        verbose_name="Tipo"
    )
    mensagem = models.TextField(verbose_name="Mensagem")
    data_envio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Envio")

    class Meta:
        verbose_name = "Mensagem de Contato"
        verbose_name_plural = "Mensagens de Contato"
        ordering = ['-data_envio']

    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"


class Empresa(models.Model):
    # Relação com o Usuário e Contato
    donos = models.ManyToManyField(
        User, 
        related_name='empresas',
        verbose_name="Donos / Gestores"
    )
    telefone = models.CharField(
        max_length=20, 
        verbose_name="Telefone",
        blank=True, 
        null=True
    )

    # Opções para os campos de seleção
    PORTE_CHOICES = [
        ('micro', 'Microempresa'),
        ('pequena', 'Pequena Empresa'),
        ('media', 'Média Empresa'),
    ]

    FUNCIONARIOS_CHOICES = [
        ('1-9', 'Até 9 funcionários'),
        ('10-49', '10 a 49 funcionários'),
        ('50-99', '50 a 99 funcionários'),
        ('100+', '100 ou mais funcionários'),
    ]

    SEGMENTO_CHOICES = [
        ('restaurante', 'Restaurante'),
        ('lanchonete', 'Lanchonete / Fast Food'),
        ('padaria', 'Padaria / Confeitaria'),
        ('delivery', 'Apenas Delivery'),
        ('bar', 'Bar / Boteco'),
        ('outros', 'Outros do ramo alimentício'),
    ]

    # Perguntas Abertas
    nome_empresa = models.CharField(
        max_length=150,
        verbose_name="Nome da Empresa"
    )
    cidade_estado = models.CharField(
        max_length=100,
        verbose_name="Cidade - Estado"
    )

    # Dados da Empresa (Campos de Escolha)
    porte = models.CharField(
        max_length=20,
        choices=PORTE_CHOICES,
        default='micro',
        verbose_name="Porte da Empresa"
    )
    numero_funcionarios = models.CharField(
        max_length=20,
        choices=FUNCIONARIOS_CHOICES,
        default='1-9',
        verbose_name="Número de Funcionários"
    )
    segmento = models.CharField(
        max_length=50,
        choices=SEGMENTO_CHOICES,
        default='restaurante',
        verbose_name="Segmento da Empresa"
    )

    def __str__(self):
        return self.nome_empresa