from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class PerfilComunidade(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil_comunidade",
        verbose_name="Usuário"
    )
    biografia = models.CharField(max_length=250, blank=True, verbose_name="Biografia")
    foto = models.ImageField(upload_to="comunidade/perfis/", blank=True, null=True, verbose_name="Foto de perfil")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")

    class Meta:
        verbose_name = "Perfil da Comunidade"
        verbose_name_plural = "Perfis da Comunidade"

    def __str__(self):
        return f"Perfil de {self.usuario.get_full_name() or self.usuario.username}"


class Publicacao(models.Model):
    CATEGORIA_CHOICES = [
        ("conquista", "Conquista"),
        ("meta", "Meta alcançada"),
        ("ideia", "Ideia ou iniciativa"),
        ("duvida", "Dúvida ou discussão"),
    ]

    autor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="publicacoes",
        verbose_name="Autor"
    )
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default="ideia", verbose_name="Categoria")
    conteudo = models.TextField(blank=True, verbose_name="Conteúdo")
    imagem = models.ImageField(upload_to="comunidade/publicacoes/", blank=True, null=True, verbose_name="Imagem")
    data_publicacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de publicação")
    data_edicao = models.DateTimeField(auto_now=True, verbose_name="Última edição")

    class Meta:
        verbose_name = "Publicação"
        verbose_name_plural = "Publicações"
        ordering = ["-data_publicacao"]

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.autor.get_full_name() or self.autor.username}"

    def clean(self):
        super().clean()
        if not (self.conteudo or "").strip() and not self.imagem:
            raise ValidationError("A publicação precisa conter um texto ou uma imagem.")


class Curtida(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="curtidas", verbose_name="Usuário")
    publicacao = models.ForeignKey(Publicacao, on_delete=models.CASCADE, related_name="curtidas", verbose_name="Publicação")
    data_curtida = models.DateTimeField(auto_now_add=True, verbose_name="Data da curtida")

    class Meta:
        verbose_name = "Curtida"
        verbose_name_plural = "Curtidas"
        ordering = ["-data_curtida"]
        constraints = [
            models.UniqueConstraint(fields=["usuario", "publicacao"], name="curtida_unica_por_usuario")
        ]


class Comentario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comentarios", verbose_name="Autor")
    publicacao = models.ForeignKey(Publicacao, on_delete=models.CASCADE, related_name="comentarios", verbose_name="Publicação")
    comentario_pai = models.ForeignKey("self", on_delete=models.CASCADE, related_name="respostas", blank=True, null=True)
    conteudo = models.TextField(max_length=2000, verbose_name="Conteúdo")
    data_comentario = models.DateTimeField(auto_now_add=True, verbose_name="Data do comentário")

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ["data_comentario"]


class Compartilhamento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="compartilhamentos")
    publicacao = models.ForeignKey(Publicacao, on_delete=models.CASCADE, related_name="compartilhamentos")
    data_compartilhamento = models.DateTimeField(auto_now_add=True)


class Notificacao(models.Model):
    TIPO_CHOICES = [
        ("curtida", "Nova curtida"),
        ("comentario", "Novo comentário"),
        ("resposta", "Nova resposta"),
        ("compartilhamento", "Novo compartilhamento"),
    ]
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificacoes_recebidas")
    remetente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notificacoes_enviadas")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    publicacao = models.ForeignKey(Publicacao, on_delete=models.CASCADE, related_name="notificacoes", blank=True, null=True)
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)


class Denuncia(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("analisando", "Em análise"),
        ("resolvida", "Resolvida"),
        ("rejeitada", "Rejeitada"),
    ]
    denunciante = models.ForeignKey(User, on_delete=models.CASCADE, related_name="denuncias_realizadas")
    publicacao = models.ForeignKey(Publicacao, on_delete=models.CASCADE, related_name="denuncias", blank=True, null=True)
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, related_name="denuncias", blank=True, null=True)
    motivo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    data_denuncia = models.DateTimeField(auto_now_add=True)
    data_analise = models.DateTimeField(blank=True, null=True)