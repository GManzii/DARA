from django.db import models
from core.models import Funcionario
from django.core.exceptions import ValidationError


class PerfilComunidade(models.Model):
    funcionario = models.OneToOneField(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="perfil_comunidade",
        verbose_name="Funcionário"
    )

    biografia = models.CharField(
        max_length=250,
        blank=True,
        verbose_name="Biografia"
    )

    foto = models.ImageField(
        upload_to="comunidade/perfis/",
        blank=True,
        null=True,
        verbose_name="Foto de perfil"
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de criação"
    )

    class Meta:
        verbose_name = "Perfil da Comunidade"
        verbose_name_plural = "Perfis da Comunidade"

    def __str__(self):
        return f"Perfil de {self.funcionario.usuario.get_full_name()}"


class Publicacao(models.Model):

    CATEGORIA_CHOICES = [
        ("conquista", "Conquista"),
        ("meta", "Meta alcançada"),
        ("ideia", "Ideia ou iniciativa"),
        ("duvida", "Dúvida ou discussão"),
    ]

    autor = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="publicacoes",
        verbose_name="Autor"
    )

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        verbose_name="Categoria"
    )

    conteudo = models.TextField(
        blank=True,
        verbose_name="Conteúdo"
    )

    imagem = models.ImageField(
        upload_to="comunidade/publicacoes/",
        blank=True,
        null=True,
        verbose_name="Imagem"
    )

    data_publicacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de publicação"
    )

    data_edicao = models.DateTimeField(
        auto_now=True,
        verbose_name="Última edição"
    )

    class Meta:
        verbose_name = "Publicação"
        verbose_name_plural = "Publicações"
        ordering = ["-data_publicacao"]

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.autor.usuario.get_full_name()}"
    def clean(self):
        super().clean()

        if not (self.conteudo or "").strip() and not self.imagem:
            raise ValidationError(
                "A publicação precisa conter um texto ou uma imagem."
            )


class Curtida(models.Model):

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="curtidas",
        verbose_name="Funcionário"
    )

    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name="curtidas",
        verbose_name="Publicação"
    )

    data_curtida = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da curtida"
    )

    class Meta:
        verbose_name = "Curtida"
        verbose_name_plural = "Curtidas"
        ordering = ["-data_curtida"]
        constraints = [
            models.UniqueConstraint(
                fields=["funcionario", "publicacao"],
                name="curtida_unica_por_funcionario"
            )
        ]

    def __str__(self):
        return f"{self.funcionario.usuario.get_full_name()} curtiu uma publicação"

class Comentario(models.Model):

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="comentarios",
        verbose_name="Autor"
    )

    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name="comentarios",
        verbose_name="Publicação"
    )

    comentario_pai = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="respostas",
        blank=True,
        null=True,
        verbose_name="Comentário respondido"
    )

    conteudo = models.TextField(
        max_length=2000,
        verbose_name="Conteúdo"
    )

    data_comentario = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do comentário"
    )

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ["data_comentario"]

    def clean(self):
        super().clean()

        if self.comentario_pai:
            if self.comentario_pai.publicacao_id != self.publicacao_id:
                raise ValidationError(
                    "A resposta precisa pertencer à mesma publicação do comentário original."
                )

            if self.comentario_pai.comentario_pai:
                raise ValidationError(
                    "Não é permitido responder a uma resposta."
                )

    def __str__(self):
        return f"Comentário de {self.funcionario.usuario.get_full_name()}"

class Compartilhamento(models.Model):

    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="compartilhamentos",
        verbose_name="Funcionário"
    )

    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name="compartilhamentos",
        verbose_name="Publicação compartilhada"
    )

    data_compartilhamento = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do compartilhamento"
    )

    class Meta:
        verbose_name = "Compartilhamento"
        verbose_name_plural = "Compartilhamentos"
        ordering = ["-data_compartilhamento"]

    def __str__(self):
        return f"{self.funcionario.usuario.get_full_name()} compartilhou uma publicação"

class Notificacao(models.Model):

    TIPO_CHOICES = [
        ("curtida", "Nova curtida"),
        ("comentario", "Novo comentário"),
        ("resposta", "Nova resposta"),
        ("compartilhamento", "Novo compartilhamento"),
    ]

    destinatario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="notificacoes_recebidas",
        verbose_name="Destinatário"
    )

    remetente = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="notificacoes_enviadas",
        verbose_name="Remetente"
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de notificação"
    )

    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name="notificacoes",
        blank=True,
        null=True,
        verbose_name="Publicação relacionada"
    )

    lida = models.BooleanField(
        default=False,
        verbose_name="Lida"
    )

    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de criação"
    )

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ["-data_criacao"]

    def clean(self):
        super().clean()

        if self.destinatario_id == self.remetente_id:
            raise ValidationError(
                "Um funcionário não pode enviar uma notificação para si mesmo."
            )

    def __str__(self):
        return (
            f"{self.remetente.usuario.get_full_name()} "
            f"- {self.get_tipo_display()}"
        )

class Denuncia(models.Model):

    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("analisando", "Em análise"),
        ("resolvida", "Resolvida"),
        ("rejeitada", "Rejeitada"),
    ]

    denunciante = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name="denuncias_realizadas",
        verbose_name="Denunciante"
    )

    publicacao = models.ForeignKey(
        Publicacao,
        on_delete=models.CASCADE,
        related_name="denuncias",
        blank=True,
        null=True,
        verbose_name="Publicação denunciada"
    )

    comentario = models.ForeignKey(
        Comentario,
        on_delete=models.CASCADE,
        related_name="denuncias",
        blank=True,
        null=True,
        verbose_name="Comentário denunciado"
    )

    motivo = models.CharField(
        max_length=150,
        verbose_name="Motivo da denúncia"
    )

    descricao = models.TextField(
        blank=True,
        verbose_name="Descrição adicional"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente",
        verbose_name="Status"
    )

    data_denuncia = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data da denúncia"
    )

    data_analise = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data da análise"
    )

    class Meta:
        verbose_name = "Denúncia"
        verbose_name_plural = "Denúncias"
        ordering = ["-data_denuncia"]

    def clean(self):
        super().clean()

        if bool(self.publicacao_id) == bool(self.comentario_id):
            raise ValidationError(
                "A denúncia deve estar relacionada a uma publicação ou a um comentário, mas não aos dois."
            )

    def __str__(self):
        return (
            f"Denúncia de {self.denunciante.usuario.get_full_name()} "
            f"- {self.get_status_display()}"
        )
