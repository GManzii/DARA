from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import ContatoForm, EmpresaForm, UsuarioDonoForm


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
    if request.method == 'POST':
        user_form = UsuarioDonoForm(request.POST)
        empresa_form = EmpresaForm(request.POST)

        if user_form.is_valid() and empresa_form.is_valid():
            # 1. Salva o Usuário (Django User)
            email = user_form.cleaned_data['email']
            senha = user_form.cleaned_data['senha']
            nome_completo = user_form.cleaned_data['nome_completo']
            telefone = user_form.cleaned_data['telefone']

            # Cria o usuário com o e-mail como username
            user = User.objects.create_user(
                username=email,
                email=email,
                password=senha,
                first_name=nome_completo
            )

            # 2. Salva a Empresa e atrela ao Usuário recém-criado
            empresa = empresa_form.save(commit=False)
            empresa.telefone = telefone
            empresa.save()

            # Adiciona o usuário na lista de donos (ManyToManyField)
            empresa.donos.add(user)

            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('area_dono')
    else:
        user_form = UsuarioDonoForm()
        empresa_form = EmpresaForm()

    context = {
        'user_form': user_form,
        'empresa_form': empresa_form
    }
    return render(request, 'core/area_dono.html', context)

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
