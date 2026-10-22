from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('escolher-perfil/', views.escolher_perfil, name='escolher_perfil'),
    path('dono/', views.area_dono, name='area_dono'),
    path('funcionario/', views.area_funcionario, name='area_funcionario'),
    path("about/", views.about, name="about"),
    path("faleconosco/", views.contact, name="contact"), 
    path('dono/', views.area_dono, name='area_dono'),
    path('questionario-esg/', views.questionario_esg, name='questionario_esg'),
    #apagar essa url depois
    path('trocar-perfil/', views.trocar_perfil, name='trocar_perfil'),
    path('perfil/', views.perfil, name='perfil'),
    path('pilares/', views.pilares, name='pilares'),
]
