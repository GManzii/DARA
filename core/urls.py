from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import EntrarForm

urlpatterns = [
    path("", views.landing, name="landing"),
    path("inicio/", views.home, name="home"),
    path('entrar/', auth_views.LoginView.as_view(
        template_name='core/entrar.html',
        authentication_form=EntrarForm,
        redirect_authenticated_user=True,
    ), name='entrar'),
    path('sair/', auth_views.LogoutView.as_view(), name='sair'),
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
