from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import ContatoForm, EmpresaForm, UsuarioDonoForm, QuestionarioESGForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

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
            # 1. Cria o Usuário
            email = user_form.cleaned_data['email']
            senha = user_form.cleaned_data['senha']
            nome_completo = user_form.cleaned_data['nome_completo']
            telefone = user_form.cleaned_data['telefone']

            user = User.objects.create_user(
                username=email,
                email=email,
                password=senha,
                first_name=nome_completo
            )

            # 2. Cria a Empresa e associa ao Usuário
            empresa = empresa_form.save(commit=False)
            empresa.telefone = telefone
            empresa.save()
            empresa.donos.add(user)

            # 3. Loga o usuário automaticamente para continuar o fluxo
            login(request, user)

            messages.success(request, "Conta e empresa criadas! Agora responda o questionário inicial.")
            return redirect('questionario_esg')
    else:
        user_form = UsuarioDonoForm()
        empresa_form = EmpresaForm()

    context = {
        'user_form': user_form,
        'empresa_form': empresa_form
    }
    return render(request, 'core/area_dono.html', context)


def questionario_esg(request):
    # Garante que só usuários logados com empresa cadastrada respondam
    if not request.user.is_authenticated:
        return redirect('area_dono')

    # Pega a empresa vinculada ao usuário logado
    empresa = request.user.empresas.first()

    if request.method == 'POST':
        form = QuestionarioESGForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            # Marca na sessão que o formulário/questionário foi preenchido com sucesso
            request.session['questionario_preenchido'] = True
            messages.success(request, "Questionário ESG salvo com sucesso! Cadastro concluído.")
            return redirect('about')  # Depois mudaremos para o Perfil/Dashboard
    else:
        form = QuestionarioESGForm(instance=empresa)

    context = {
        'form': form,
        'empresa': empresa
    }
    return render(request, 'core/questionario_esg.html', context)

def area_funcionario(request):
    return render(request, 'core/area_funcionario.html')


def about(request):
    # Passa a informação se o questionário foi respondido para liberar o link dos pilares
    exibir_pilares = request.session.get('questionario_preenchido', False)
    return render(request, "core/about.html", {'exibir_pilares': exibir_pilares})


def pilares(request):
    return render(request, 'core/pilares.html')


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

@login_required
def perfil(request):
    # Procura a empresa associada ao utilizador logado
    empresa = request.user.empresas.first()
    
    context = {
        'usuario': request.user,
        'empresa': empresa,
    }
    return render(request, 'core/perfil.html', context)