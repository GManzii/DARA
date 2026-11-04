from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import ContatoForm, EmpresaForm, UsuarioDonoForm, QuestionarioESGForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Empresa
from django.http import JsonResponse

def landing(request):
    return render(request, 'core/landing.html')

def home(request):
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
                "Questionário preenchido! Agora vamos criar sua conta."
            )

            return redirect('area_dono')

    else:
        form = QuestionarioESGForm()

    return render(
        request,
        'core/questionario_esg.html',
        {'form': form}
    )

def cadastro_funcionario(request):
    return render(request, 'core/cadastro_funcionario.html')

def area_funcionario(request):
    return render(request, 'core/area_funcionario.html')


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

    context = {
        'usuario': request.user,
        'empresa': empresa,
        'total_funcionarios': 0,
        'total_documentos': 0,
        'total_metas': 0,
        'total_comunidades': 0,
    }
    return render(request, 'core/perfil.html', context)