from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from .models import Publicacao

def usuario_tem_acesso_comunidade(usuario):
    if usuario.empresas.exists():
        return True
    funcionario = getattr(usuario, "perfil_funcionario", None)
    if funcionario and funcionario.acesso_comunidade:
        return True
    return False

def comunidade_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not usuario_tem_acesso_comunidade(request.user):
            raise PermissionDenied("Você não tem autorização para acessar a Comunidade DARA.")
        return view_func(request, *args, **kwargs)
    return wrapper

@comunidade_required
def feed(request):
    # Processa o formulário quando clicas em "Publicar"
    if request.method == 'POST':
        conteudo = request.POST.get('texto')
        if conteudo:
            funcionario = getattr(request.user, "perfil_funcionario", None)
            if funcionario:
                Publicacao.objects.create(
                    autor=funcionario, 
                    conteudo=conteudo,
                    categoria='ideia'
                )
            return redirect('comunidade_feed')

    # Vai buscar as publicações para mostrar na página
    postagens = Publicacao.objects.all()
    return render(request, "comunidade/feed.html", {'postagens': postagens})