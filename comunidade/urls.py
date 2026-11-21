from django.urls import path
from . import views

urlpatterns = [
    path("", views.feed, name="comunidade_feed"),
    path("excluir/<int:publicacao_id>/", views.excluir_publicacao, name="comunidade_excluir"),
]