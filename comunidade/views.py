from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


def usuario_tem_acesso_comunidade(usuario):
    # Verifica se é proprietário de alguma empresa
    if usuario.empresas.exists():
        return True

    # Verifica se é funcionário
    funcionario = getattr(usuario, "perfil_funcionario", None)

    if funcionario and funcionario.acesso_comunidade:
        return True

    return False


def comunidade_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if not usuario_tem_acesso_comunidade(request.user):
            raise PermissionDenied(
                "Você não tem autorização para acessar a Comunidade DARA."
            )

        return view_func(request, *args, **kwargs)

    return wrapper

@comunidade_required
def feed(request):
    return render(request, "comunidade/feed.html")