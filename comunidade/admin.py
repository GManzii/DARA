from django.contrib import admin
from .models import (
    PerfilComunidade,
    Publicacao,
    Curtida,
    Comentario,
    Compartilhamento,
    Notificacao,
    Denuncia,
)


@admin.register(PerfilComunidade)
class PerfilComunidadeAdmin(admin.ModelAdmin):
    list_display = ("usuario", "data_criacao")
    search_fields = ("usuario__username", "usuario__first_name", "usuario__last_name")


@admin.register(Publicacao)
class PublicacaoAdmin(admin.ModelAdmin):
    list_display = ("autor", "categoria", "data_publicacao")
    list_filter = ("categoria", "data_publicacao")
    search_fields = ("conteudo", "autor__username", "autor__first_name")


@admin.register(Curtida)
class CurtidaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "publicacao", "data_curtida")
    list_filter = ("data_curtida",)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "publicacao", "comentario_pai", "data_comentario")
    list_filter = ("data_comentario",)
    search_fields = ("conteudo", "usuario__username", "usuario__first_name")


@admin.register(Compartilhamento)
class CompartilhamentoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "publicacao", "data_compartilhamento")


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("destinatario", "remetente", "tipo", "lida", "data_criacao")
    list_filter = ("tipo", "lida", "data_criacao")


@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ("denunciante", "motivo", "status", "data_denuncia")
    list_filter = ("status", "data_denuncia")
    search_fields = ("motivo", "descricao", "denunciante__username")