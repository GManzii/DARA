from django.contrib import admin
from .models import MensagemContato, Conversa, Mensagem

@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'tipo', 'data_envio')
    list_filter = ('tipo', 'data_envio')
    search_fields = ('nome', 'email', 'mensagem')
    readonly_fields = ('data_envio',)

@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'empresa', 'criada_em')
    list_filter = ('tipo',)
    filter_horizontal = ('participantes',)


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ('conversa', 'autor', 'criada_em')
    list_filter = ('conversa',)
    search_fields = ('texto',)
