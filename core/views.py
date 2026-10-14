
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContatoForm


def home(request):
    # Se já escolheu um perfil, direciona para a área correspondente
    perfil = request.session.get('perfil')

    if perfil == 'dono':
        return redirect('area_dono')
    elif perfil == 'funcionario':
        return redirect('area_funcionario')

    # Se ainda não escolheu, mostra a página inicial
    return render(request, "core/home.html")


def escolher_perfil(request):
    if request.method == 'POST':
        perfil = request.POST.get('perfil')

        if perfil in ['dono', 'funcionario']:
            request.session['perfil'] = perfil

            if perfil == 'dono':
                return redirect('area_dono')
            else:
                return redirect('area_funcionario')

    return redirect('home')


def area_dono(request):
    return render(request, 'core/area_dono.html')


def area_funcionario(request):
    return render(request, 'core/area_funcionario.html')


def about(request):
    return render(request, "core/about.html")


def contact(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Sua mensagem foi enviada com sucesso!'
            )
            return redirect('contact')
    else:
        form = ContatoForm()

    return render(
        request,
        'core/faleconosco.html',
        {'form': form}
    )
#apagar essa funcao depois, ela serve para limpar a escolha de dono ou funcionario (usar apenas no desenvolvimento)
def trocar_perfil(request):
    request.session.pop('perfil', None)
    return redirect('home')
