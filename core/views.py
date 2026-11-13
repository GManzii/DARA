from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import (
    ContatoForm,
    EmpresaForm,
    UsuarioDonoForm,
    QuestionarioESGForm,
    UsuarioFuncionarioForm,
    DocumentoForm
)
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Empresa, Funcionario, Documento
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.urls import reverse

class LoginPersonalizadoView(LoginView):

    def get_success_url(self):

        usuario = self.request.user

        # Verifica se é funcionário
        if hasattr(usuario, 'perfil_funcionario'):
            return reverse('area_funcionario')

        # Dono ou outro usuário autenticado
        return reverse('home')

def landing(request):
    return render(request, 'core/landing.html')

def home(request):
    if request.user.is_authenticated and hasattr(request.user, 'perfil_funcionario'):
        return redirect('area_funcionario')
    # Se já escolheu um perfil, direciona para a área correspondente
    perfil = request.session.get('perfil')

    # if perfil == 'dono':
    #     return redirect('area_dono')
    # elif perfil == 'funcionario':
    #     return redirect('area_funcionario')

    # # Se ainda não escolheu, mostra a página inicial
    # Quem já entrou vê os pilares; quem não entrou vê a tela de boas-vindas
    if request.user.is_authenticated:
        return render(request, "core/home.html")
    return render(request, "core/boas_vindas.html")

def escolher_perfil(request):
    if request.method == 'POST':
        perfil = request.POST.get('perfil')

        if perfil == 'dono':
            request.session['perfil'] = 'dono'
            return redirect('area_dono')

        elif perfil == 'funcionario':
            return redirect('cadastro_funcionario')

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
    if request.method == 'POST':
        form = QuestionarioESGForm(request.POST)

        if form.is_valid():
            respostas = form.cleaned_data

            request.session['respostas_esg'] = respostas

            messages.success(
                request,
                "Questionário preenchido, Bem vindo à sua conta!"
            )

            return redirect('home')

    else:
        form = QuestionarioESGForm()

    return render(
        request,
        'core/questionario_esg.html',
        {'form': form}
    )

def cadastro_funcionario(request):

    # Impede que um usuário já autenticado crie outra conta
    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil_funcionario'):
            return redirect('area_funcionario')

        return redirect('home')

    if request.method == 'POST':
        form = UsuarioFuncionarioForm(request.POST)

        if form.is_valid():
            dados = form.cleaned_data

            # Localiza a empresa pelo código de convite
            empresa = Empresa.objects.get(
                codigo_convite=dados['codigo_convite']
            )

            try:
                with transaction.atomic():

                    # Cria a conta do funcionário
                    usuario = User.objects.create_user(
                        username=dados['email'],
                        email=dados['email'],
                        password=dados['senha'],
                        first_name=dados['nome_completo']
                    )

                    # Vincula o funcionário à empresa
                    Funcionario.objects.create(
                        usuario=usuario,
                        empresa=empresa
                    )

                # Realiza o login automaticamente
                login(request, usuario)

                messages.success(
                    request,
                    f"Cadastro realizado! Você agora faz parte da equipe da {empresa.nome_empresa}."
                )

                return redirect('area_funcionario')

            except Exception:
                messages.error(
                    request,
                    "Não foi possível concluir o cadastro. Tente novamente."
                )

    else:
        form = UsuarioFuncionarioForm()

    return render(
        request,
        'core/cadastro_funcionario.html',
        {'form': form}
    )

@login_required(login_url='entrar')
def area_funcionario(request):

    if not hasattr(request.user, 'perfil_funcionario'):
        messages.error(
            request,
            "Esta área é exclusiva para funcionários."
        )
        return redirect('home')

    funcionario = request.user.perfil_funcionario

    contexto = {
        'funcionario': funcionario,
        'empresa': funcionario.empresa,
    }

    return render(
        request,
        'core/area_funcionario.html',
        contexto
    )


def about(request):
    # Passa a informação se o questionário foi respondido para liberar o link dos pilares
    exibir_pilares = request.session.get('questionario_preenchido', False)
    return render(request, "core/about.html", {'exibir_pilares': exibir_pilares})




def pilares(request):
    empresa = None

    if request.user.is_authenticated:
        empresa = request.user.empresas.first()

    # Ações organizadas por pilar
    pilares_acoes = {
        'ambiental': [
            {
                'campo': 'esg_01_higiene_manipulacao',
                'titulo': 'Higiene e Manipulação Segura',
                'descricao': 'Garantir que 100% da equipe siga as normas de higiene e controle de temperatura dos alimentos.',
            },
            {
                'campo': 'esg_02_separacao_lixo',
                'titulo': 'Separação Simples de Lixo',
                'descricao': 'Lixeiras separadas para resíduos orgânicos e recicláveis na cozinha e no atendimento.',
            },
            {
                'campo': 'esg_03_coleta_oleo',
                'titulo': 'Coleta de Óleo Usado',
                'descricao': 'Armazenar o óleo de fritura em recipientes adequados e entregar a coletores credenciados.',
            },
            {
                'campo': 'esg_04_combate_desperdicio',
                'titulo': 'Combate ao Desperdício Visível',
                'descricao': 'Avisos amigáveis para conscientizar clientes sobre o desperdício em buffets ou pratos.',
            },
            {
                'campo': 'esg_06_recibos_digitais',
                'titulo': 'Comandas e Recibos Digitais',
                'descricao': 'Adotar comandas eletrônicas e enviar nota fiscal por e-mail ou WhatsApp para poupar papel.',
            },
            {
                'campo': 'esg_07_aeradores_torneiras',
                'titulo': 'Aeradores nas Torneiras',
                'descricao': 'Instalar adaptadores de vazão nas pias da cozinha e nos banheiros para poupar água.',
            },
            {
                'campo': 'esg_09_descarte_lampadas_baterias',
                'titulo': 'Descarte de Lâmpadas e Baterias',
                'descricao': 'Separar lâmpadas queimadas e pilhas para destinação em pontos de coleta da cidade.',
            },
            {
                'campo': 'esg_11_apagando_luz',
                'titulo': 'Rotina Apagando Luz',
                'descricao': 'Procedimento para desligar luzes e aparelhos em estoques, vestiários e ambientes vazios.',
            },
            {
                'campo': 'esg_12_uso_consciente_embalagens',
                'titulo': 'Uso Consciente de Embalagens',
                'descricao': 'Perguntar no delivery se o cliente realmente precisa de talheres e guardanapos descartáveis.',
            },
            {
                'campo': 'esg_14_troca_descartaveis',
                'titulo': 'Troca Gradual de Descartáveis',
                'descricao': 'Substituir recipientes de plástico por embalagens de papel kraft ou biodegradáveis.',
            },
            {
                'campo': 'esg_16_compra_produtor_local',
                'titulo': 'Compra na Feira / Produtor Local',
                'descricao': 'Comprar ingredientes hortifrúti diretamente de feirantes ou agricultores da região.',
            },
            {
                'campo': 'esg_18_compostagem_basica',
                'titulo': 'Compostagem Básica',
                'descricao': 'Encaminhar restos vegetais e cascas cruas para hortas comunitárias ou composteiras locais.',
            },
            {
                'campo': 'esg_22_equipamentos_inverter',
                'titulo': 'Equipamentos Inverter / Eficientes',
                'descricao': 'Trocar geladeiras e freezers antigos por modelos com selo Procel A ou tecnologia Inverter.',
            },
            {
                'campo': 'esg_25_energia_solar',
                'titulo': 'Energia Solar (Alugada ou Própria)',
                'descricao': 'Aderir a cooperativas regionais de energia solar para consumir eletricidade 100% limpa.',
            },
        ],

        'social': [
            {
                'campo': 'esg_05_cardapio_transparente',
                'titulo': 'Cardápio Transparente',
                'descricao': 'Sinalizar claramente ingredientes, pratos vegetarianos/veganos e presença de alergênicos.',
            },
            {
                'campo': 'esg_13_doacao_excedente',
                'titulo': 'Doação do Excedente Limpo',
                'descricao': 'Parceria com ONGs para doação segura de alimentos preparados que não foram servidos.',
            },
            {
                'campo': 'esg_15_apoio_anti_lesao',
                'titulo': 'Compressas e Apoio Anti-Lesão',
                'descricao': 'Pausas ativas e orientação postural para cozinheiros e atendentes que passam horas em pé.',
            },
            {
                'campo': 'esg_19_folga_aniversario_bem_estar',
                'titulo': 'Folga de Aniversário ou Benefício',
                'descricao': 'Oferecer folga no aniversário ou pequenos incentivos de saúde/estudo para os funcionários.',
            },
            {
                'campo': 'esg_20_treinamento_diversidade',
                'titulo': 'Treinamento Sobre Diversidade',
                'descricao': 'Orientar a equipe sobre respeito e atendimento inclusivo a todos os perfis de clientes.',
            },
            {
                'campo': 'esg_23_opcoes_plant_based',
                'titulo': 'Opções Plant-Based no Cardápio',
                'descricao': 'Desenvolver e promover pratos saborosos 100% à base de plantas para incentivar a redução de carne.',
            },
        ],

        'governanca': [
            {
                'campo': 'esg_08_organizacao_pvps',
                'titulo': 'Organização PVPS no Estoque',
                'descricao': "Aplicar a regra 'Primeiro que Vence, Primeiro que Sai' para evitar perdas de insumos.",
            },
            {
                'campo': 'esg_10_caixa_sugestoes',
                'titulo': 'Caixa de Sugestões / Denúncias',
                'descricao': 'Canal simples (caixinha física ou WhatsApp) para escutar a equipe de forma confidencial.',
            },
            {
                'campo': 'esg_17_planilha_perdas',
                'titulo': 'Planilha de Perdas na Produção',
                'descricao': 'Pesar e registrar o desperdício diário do pré-preparo para ajustar o volume de compras.',
            },
            {
                'campo': 'esg_21_ovos_cage_free_compra_etica',
                'titulo': 'Ovos Cage-Free e Compra Ética',
                'descricao': 'Priorizar ovos de galinhas livres de gaiola e carnes de fornecedores com certificado de manejo.',
            },
            {
                'campo': 'esg_24_selo_certificacao_local',
                'titulo': 'Selo ou Certificação Local',
                'descricao': 'Obter selos municipais de sustentabilidade, qualidade sanitária ou Lixo Zero.',
            },
        ],
    }

    # Salva somente as ações do pilar enviado
    if request.method == 'POST' and empresa:
        nome_pilar = request.POST.get('pilar')

        if nome_pilar not in pilares_acoes:
            return JsonResponse(
                {'success': False, 'error': 'Pilar inválido.'},
                status=400
            )

        campos = [
            acao['campo'] for acao in pilares_acoes[nome_pilar]
        ]

        for campo in campos:
            setattr(empresa, campo, campo in request.POST)

        empresa.save(update_fields=campos)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        return redirect('pilares')

    # Prepara as ações para cada pilar
    context = {
        'pode_editar': empresa is not None,
    }

    for nome_pilar, acoes in pilares_acoes.items():
        pendentes = []
        realizadas = []

        for acao in acoes:
            marcada = (
                getattr(empresa, acao['campo'], False)
                if empresa else False
            )

            acao['marcada'] = marcada

            if marcada:
                realizadas.append(acao)
            else:
                pendentes.append(acao)

        context[f'{nome_pilar}_pendentes'] = pendentes
        context[f'{nome_pilar}_realizadas'] = realizadas

    return render(request, 'core/pilares.html', context)




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

@login_required(login_url='entrar')
def perfil(request):
    # Usa 'donos' porque a relação no models.py é ManyToMany
    empresa = request.user.empresas.first()
    aba_ativa = request.GET.get('aba', 'visao_geral')

    if request.method == 'POST' and 'enviar_documento' in request.POST:
        doc_form = DocumentoForm(request.POST, request.FILES)
        if doc_form.is_valid() and empresa:
            doc = doc_form.save(commit=False)
            doc.empresa = empresa
            doc.enviado_por = request.user
            doc.save()
            messages.success(request, "Documento registrado no repositório corporativo!")
            return redirect('/perfil/?aba=documentos')
        else:
            aba_ativa = 'documentos'
    else:
        doc_form = DocumentoForm()

    documentos = list(empresa.documentos.all().order_by('-data_envio')) if empresa else []

    # Indicadores executivos de conformidade
    total_documentos = len(documentos)
    docs_vigentes = sum(1 for d in documentos if d.status == 'VIGENTE' and d.status_validade != 'vencido')
    docs_alerta = sum(1 for d in documentos if d.status_validade in ('vencido', 'atencao'))
    count_e = sum(1 for d in documentos if d.pilar == 'E')
    count_s = sum(1 for d in documentos if d.pilar == 'S')
    count_g = sum(1 for d in documentos if d.pilar == 'G')

    context = {
        'usuario': request.user,
        'empresa': empresa,
        'aba_ativa': aba_ativa,
        'doc_form': doc_form,
        'documentos': documentos,
        'total_funcionarios': Funcionario.objects.filter(empresa=empresa).count() if empresa else 0,
        'total_documentos': total_documentos,
        'docs_vigentes': docs_vigentes,
        'docs_alerta': docs_alerta,
        'count_e': count_e,
        'count_s': count_s,
        'count_g': count_g,
        'total_metas': 0,
        'total_comunidades': 0,
    }
    return render(request, 'core/perfil.html', context)


@login_required(login_url='entrar')
def excluir_documento(request, doc_id):
    empresa = request.user.empresas.first()
    documento = get_object_or_404(Documento, id=doc_id, empresa=empresa)
    documento.arquivo.delete(save=False)
    documento.delete()
    messages.success(request, "Documento removido do repositório.")
    return redirect('/perfil/?aba=documentos')