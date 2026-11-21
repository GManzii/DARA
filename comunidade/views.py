from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
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
    if request.method == 'POST':
        conteudo = request.POST.get('texto', '').strip()
        categoria = request.POST.get('categoria', 'ideia')
        if conteudo:
            Publicacao.objects.create(
                autor=request.user,
                conteudo=conteudo,
                categoria=categoria
            )
            return redirect('comunidade_feed')

    postagens = Publicacao.objects.select_related('autor').all()

    empresa = request.user.empresas.first()
    if empresa:
        cargo_usuario = "Gestor(a) de sustentabilidade"
        empresa_nome = (
            getattr(empresa, "nome_fantasia", None)
            or getattr(empresa, "razao_social", None)
            or str(empresa)
        )
    else:
        func = getattr(request.user, "perfil_funcionario", None)
        cargo_usuario = getattr(func, "cargo", "Colaborador(a)")
        emp_func = getattr(func, "empresa", None)
        empresa_nome = (
            (
                getattr(emp_func, "nome_fantasia", None)
                or getattr(emp_func, "razao_social", None)
                or str(emp_func)
            )
            if emp_func
            else "DARA ESG"
        )

    context = {
        'postagens': postagens,
        'cargo_usuario': cargo_usuario,
        'empresa_nome': empresa_nome,
        'total_publicacoes': postagens.count(),
    }
    return render(request, "comunidade/feed.html", context)


@comunidade_required
@require_POST
def excluir_publicacao(request, publicacao_id):
    publicacao = get_object_or_404(Publicacao, id=publicacao_id)
    if publicacao.autor != request.user and not request.user.is_superuser:
        raise PermissionDenied("Você não tem permissão para excluir esta publicação.")
    publicacao.delete()
    return redirect('comunidade_feed')