import json
import os
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import (
    ContatoForm,
    EmpresaForm,
    UsuarioDonoForm,
    QuestionarioESGForm,
    UsuarioFuncionarioForm,
    DocumentoForm,
    CadastroFuncionarioGestorForm,
    NovaConversaForm,
)
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Empresa, Funcionario, Conversa, Mensagem, Documento
from django.db import transaction
from django.http import JsonResponse, HttpResponse, FileResponse
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.cache import cache

from . import pedro


class LoginPersonalizadoView(LoginView):

    def get_success_url(self):
        # Volta para a página que pediu o login (ex.: o chat do Pedro)
        destino = self.get_redirect_url()
        if destino:
            return destino

        # Dono e funcionário vão para a mesma tela inicial
        return reverse('home')


def landing(request):
    return render(request, 'core/landing.html')


def home(request):
    # Quem já entrou (gestor ou funcionário) vê a tela inicial; quem não entrou vê boas-vindas
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

            empresa = empresa_form.save(commit=False)
            empresa.telefone = telefone
            empresa.save()
            empresa.donos.add(user)

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
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UsuarioFuncionarioForm(request.POST)

        if form.is_valid():
            dados = form.cleaned_data

            empresa = Empresa.objects.get(
                codigo_convite=dados['codigo_convite']
            )

            try:
                with transaction.atomic():
                    usuario = User.objects.create_user(
                        username=dados['email'],
                        email=dados['email'],
                        password=dados['senha'],
                        first_name=dados['nome_completo']
                    )

                    Funcionario.objects.create(
                        usuario=usuario,
                        empresa=empresa
                    )

                login(request, usuario)

                messages.success(
                    request,
                    f"Cadastro realizado! Você agora faz parte da equipe da {empresa.nome_empresa}."
                )

                return redirect('home')

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
        messages.error(request, "Esta área é exclusiva para funcionários.")
        return redirect('home')
    return redirect('perfil')


def about(request):
    exibir_pilares = request.session.get('questionario_preenchido', False)
    return render(request, "core/about.html", {'exibir_pilares': exibir_pilares})


def pilares(request):
    empresa = None
    eh_funcionario = False

    if request.user.is_authenticated:
        if hasattr(request.user, 'perfil_funcionario') and request.user.perfil_funcionario is not None:
            eh_funcionario = True
            empresa = request.user.perfil_funcionario.empresa
        else:
            empresa = request.user.empresas.first()

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

    if request.method == 'POST' and empresa and not eh_funcionario:
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

    context = {
        'pode_editar': (empresa is not None and not eh_funcionario),
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


def trocar_perfil(request):
    request.session.pop('perfil', None)
    return redirect('home')


@login_required(login_url='entrar')
def perfil(request):
    eh_funcionario = hasattr(request.user, 'perfil_funcionario') and request.user.perfil_funcionario is not None

    # =======================================================================
    # PERFIL DO FUNCIONÁRIO (abre core/area_funcionario.html no botão Perfil)
    # =======================================================================
    if eh_funcionario:
        funcionario = request.user.perfil_funcionario
        empresa = funcionario.empresa

        catalogo_esg = [
            # Ambiental (E)
            ('E', 'Ambiental (E)', 'ambiental', 'esg_01_higiene_manipulacao', 'Higiene e Manipulação Segura', 'Garantir que 100% da equipe siga as normas de higiene e controle de temperatura dos alimentos.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_02_separacao_lixo', 'Separação Simples de Lixo', 'Lixeiras separadas para resíduos orgânicos e recicláveis na cozinha e no atendimento.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_03_coleta_oleo', 'Coleta de Óleo Usado', 'Armazenar o óleo de fritura em recipientes adequados e entregar a coletores credenciados.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_04_combate_desperdicio', 'Combate ao Desperdício Visível', 'Avisos amigáveis para conscientizar clientes sobre o desperdício em buffets ou pratos.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_06_recibos_digitais', 'Comandas e Recibos Digitais', 'Adotar comandas eletrônicas e enviar nota fiscal por e-mail ou WhatsApp para poupar papel.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_07_aeradores_torneiras', 'Aeradores nas Torneiras', 'Instalar adaptadores de vazão nas pias da cozinha e nos banheiros para poupar água.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_09_descarte_lampadas_baterias', 'Descarte de Lâmpadas e Baterias', 'Separar lâmpadas queimadas e pilhas para destinação em pontos de coleta da cidade.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_11_apagando_luz', 'Rotina Apagando Luz', 'Procedimento para desligar luzes e aparelhos em estoques, vestiários e ambientes vazios.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_12_uso_consciente_embalagens', 'Uso Consciente de Embalagens', 'Perguntar no delivery se o cliente realmente precisa de talheres e guardanapos descartáveis.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_14_troca_descartaveis', 'Troca Gradual de Descartáveis', 'Substituir recipientes de plástico por embalagens de papel kraft ou biodegradáveis.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_16_compra_produtor_local', 'Compra na Feira / Produtor Local', 'Comprar ingredientes hortifrúti diretamente de feirantes ou agricultores da região.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_18_compostagem_basica', 'Compostagem Básica', 'Encaminhar restos vegetais e cascas cruas para hortas comunitárias ou composteiras locais.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_22_equipamentos_inverter', 'Equipamentos Inverter / Eficientes', 'Trocar geladeiras e freezers antigos por modelos com selo Procel A ou tecnologia Inverter.'),
            ('E', 'Ambiental (E)', 'ambiental', 'esg_25_energia_solar', 'Energia Solar (Alugada ou Própria)', 'Aderir a cooperativas regionais de energia solar para consumir eletricidade 100% limpa.'),
            # Social (S)
            ('S', 'Social (S)', 'social', 'esg_05_cardapio_transparente', 'Cardápio Transparente', 'Sinalizar claramente ingredientes, pratos vegetarianos/veganos e presença de alergênicos.'),
            ('S', 'Social (S)', 'social', 'esg_13_doacao_excedente', 'Doação do Excedente Limpo', 'Parceria com ONGs para doação segura de alimentos preparados que não foram servidos.'),
            ('S', 'Social (S)', 'social', 'esg_15_apoio_anti_lesao', 'Compressas e Apoio Anti-Lesão', 'Pausas ativas e orientação postural para cozinheiros e atendentes que passam horas em pé.'),
            ('S', 'Social (S)', 'social', 'esg_19_folga_aniversario_bem_estar', 'Folga de Aniversário ou Benefício', 'Oferecer folga no aniversário ou pequenos incentivos de saúde/estudo para os funcionários.'),
            ('S', 'Social (S)', 'social', 'esg_20_treinamento_diversidade', 'Treinamento Sobre Diversidade', 'Orientar a equipe sobre respeito e atendimento inclusivo a todos os perfis de clientes.'),
            ('S', 'Social (S)', 'social', 'esg_23_opcoes_plant_based', 'Opções Plant-Based no Cardápio', 'Desenvolver e promover pratos saborosos 100% à base de plantas para incentivar a redução de carne.'),
            # Governança (G)
            ('G', 'Governança (G)', 'governanca', 'esg_08_organizacao_pvps', 'Organização PVPS no Estoque', "Aplicar a regra 'Primeiro que Vence, Primeiro que Sai' para evitar perdas de insumos."),
            ('G', 'Governança (G)', 'governanca', 'esg_10_caixa_sugestoes', 'Caixa de Sugestões / Denúncias', 'Canal simples (caixinha física ou WhatsApp) para escutar a equipe de forma confidencial.'),
            ('G', 'Governança (G)', 'governanca', 'esg_17_planilha_perdas', 'Planilha de Perdas na Produção', 'Pesar e registrar o desperdício diário do pré-preparo para ajustar o volume de compras.'),
            ('G', 'Governança (G)', 'governanca', 'esg_21_ovos_cage_free_compra_etica', 'Ovos Cage-Free e Compra Ética', 'Priorizar ovos de galinhas livres de gaiola e carnes de fornecedores com certificado de manejo.'),
            ('G', 'Governança (G)', 'governanca', 'esg_24_selo_certificacao_local', 'Selo ou Certificação Local', 'Obter selos municipais de sustentabilidade, qualidade sanitária ou Lixo Zero.'),
        ]

        lista_metas = []
        resumo_pilares = {
            'ambiental': {'concluidas': 0, 'total': 0, 'percentual': 0},
            'social': {'concluidas': 0, 'total': 0, 'percentual': 0},
            'governanca': {'concluidas': 0, 'total': 0, 'percentual': 0},
        }

        for sigla, nome_pilar, chave, campo, titulo, descricao in catalogo_esg:
            concluida = bool(getattr(empresa, campo, False)) if empresa else False
            resumo_pilares[chave]['total'] += 1
            if concluida:
                resumo_pilares[chave]['concluidas'] += 1

            lista_metas.append({
                'pilar_sigla': sigla,
                'pilar_nome': nome_pilar,
                'titulo': titulo,
                'descricao': descricao,
                'concluida': concluida,
            })

        for dados in resumo_pilares.values():
            if dados['total'] > 0:
                dados['percentual'] = int((dados['concluidas'] / dados['total']) * 100)

        total_metas = len(lista_metas)
        metas_cumpridas = sum(1 for m in lista_metas if m['concluida'])
        percentual_metas = int((metas_cumpridas / total_metas) * 100) if total_metas > 0 else 0
        total_grupos = request.user.conversas.filter(tipo=Conversa.TIPO_GRUPO).count()

        contexto = {
            'usuario': request.user,
            'funcionario': funcionario,
            'empresa': empresa,
            'total_metas': total_metas,
            'metas_cumpridas': metas_cumpridas,
            'percentual_metas': percentual_metas,
            'resumo_pilares': resumo_pilares,
            'lista_metas': lista_metas,
            'total_grupos': total_grupos,
        }

        return render(request, 'core/area_funcionario.html', contexto)

    # =======================================================================
    # PERFIL DO GESTOR (core/perfil.html)
    # =======================================================================
    empresa = request.user.empresas.first()
    aba_ativa = request.GET.get('aba', 'visao_geral')

    doc_form = DocumentoForm()
    func_form = CadastroFuncionarioGestorForm()

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

    elif request.method == 'POST' and 'cadastrar_funcionario' in request.POST:
        func_form = CadastroFuncionarioGestorForm(request.POST)
        if func_form.is_valid() and empresa:
            nome = func_form.cleaned_data['nome_completo'].strip()
            partes_nome = nome.split(' ', 1)
            primeiro_nome = partes_nome[0]
            sobrenome = partes_nome[1] if len(partes_nome) > 1 else ''
            email = func_form.cleaned_data['email']
            senha = func_form.cleaned_data['senha']

            with transaction.atomic():
                novo_usuario = User.objects.create_user(
                    username=email,
                    email=email,
                    password=senha,
                    first_name=primeiro_nome,
                    last_name=sobrenome
                )
                Funcionario.objects.create(
                    usuario=novo_usuario,
                    empresa=empresa
                )

            messages.success(request, f"Colaborador(a) {nome} cadastrado(a) com sucesso!")
            return redirect('/perfil/?aba=funcionarios')
        else:
            aba_ativa = 'funcionarios'

    documentos = list(empresa.documentos.all().order_by('-data_envio')) if empresa else []
    total_documentos = len(documentos)
    docs_vigentes = sum(1 for d in documentos if d.status == 'VIGENTE' and d.status_validade != 'vencido')
    docs_alerta = sum(1 for d in documentos if d.status_validade in ('vencido', 'atencao'))
    count_e = sum(1 for d in documentos if d.pilar == 'E')
    count_s = sum(1 for d in documentos if d.pilar == 'S')
    count_g = sum(1 for d in documentos if d.pilar == 'G')

    funcionarios = list(empresa.funcionarios.select_related('usuario').all()) if empresa else []
    total_funcionarios = len(funcionarios)
    funcionarios_ativos = sum(1 for f in funcionarios if f.usuario.is_active)
    limite_30_dias = timezone.now() - timedelta(days=30)
    funcionarios_recentes = sum(1 for f in funcionarios if f.data_cadastro >= limite_30_dias)

    total_metas = 0
    metas_cumpridas = 0
    if empresa:
        campos_esg = [f.name for f in empresa._meta.get_fields() if f.name.startswith('esg_')]
        total_metas = len(campos_esg)
        for campo in campos_esg:
            if getattr(empresa, campo, False):
                metas_cumpridas += 1

    percentual_esg = metas_cumpridas / total_metas if total_metas > 0 else 0
    percentual_metas_int = int(percentual_esg * 100)

    ano_atual = timezone.now().year
    labels_anos = [str(ano_atual - i) for i in range(5, -1, -1)]
    faturamento_base = 62
    valores_sem_esg = []
    valores_com_esg = []

    for i in range(6):
        base_ano = round(faturamento_base * ((1.03) ** i))
        valores_sem_esg.append(base_ano)
        bonus_esg = 1 + (0.15 * percentual_esg * i)
        esg_ano = round(base_ano * bonus_esg)
        valores_com_esg.append(esg_ano)

    context = {
        'usuario': request.user,
        'empresa': empresa,
        'aba_ativa': aba_ativa,
        'doc_form': doc_form,
        'documentos': documentos,
        'total_documentos': total_documentos,
        'docs_vigentes': docs_vigentes,
        'docs_alerta': docs_alerta,
        'count_e': count_e,
        'count_s': count_s,
        'count_g': count_g,
        'func_form': func_form,
        'funcionarios': funcionarios,
        'total_funcionarios': total_funcionarios,
        'funcionarios_ativos': funcionarios_ativos,
        'funcionarios_recentes': funcionarios_recentes,
        'total_metas': total_metas,
        'metas_cumpridas': metas_cumpridas,
        'percentual_metas': percentual_metas_int,
        'total_comunidades': 0,
        'labels_anos': json.dumps(labels_anos),
        'valores_sem_esg': json.dumps(valores_sem_esg),
        'valores_com_esg': json.dumps(valores_com_esg),
    }

    return render(request, 'core/perfil.html', context)


# ---------------------------------------------------------------------------
# Conversas
# ---------------------------------------------------------------------------

TAMANHO_MAX_ANEXO = 10 * 1024 * 1024  # 10 MB
IMAGENS_SEGURAS = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}


def _empresa_do_usuario(usuario):
    """Empresa do usuário, seja ele funcionário ou dono. None se não tiver."""
    if hasattr(usuario, 'perfil_funcionario'):
        return usuario.perfil_funcionario.empresa
    return usuario.empresas.first()


def _eh_gerente(usuario):
    """Gerente = dono da empresa (quem pode criar chats)."""
    return (
        not hasattr(usuario, 'perfil_funcionario')
        and usuario.empresas.exists()
    )


def _garantir_pedro(usuario):
    """Todo usuário tem o seu chat com o Pedro (fica em branco por enquanto)."""
    if not Conversa.objects.filter(
        tipo=Conversa.TIPO_PEDRO, participantes=usuario
    ).exists():
        pedro = Conversa.objects.create(tipo=Conversa.TIPO_PEDRO, nome='Pedro')
        pedro.participantes.add(usuario)


def _hora_curta(momento):
    """'agora', 'HH:MM' (hoje) ou 'dd/mm' (outros dias)."""
    momento = timezone.localtime(momento)
    agora = timezone.localtime()
    if (agora - momento).total_seconds() < 60:
        return 'agora'
    if momento.date() == agora.date():
        return momento.strftime('%H:%M')
    return momento.strftime('%d/%m')


def _previa(mensagem):
    if mensagem is None:
        return 'Nenhuma mensagem ainda'
    if mensagem.texto:
        return mensagem.texto
    if mensagem.anexo_tipo == 'audio':
        return 'Mensagem de áudio'
    if mensagem.anexo_tipo == 'imagem':
        return 'Imagem'
    return f'Arquivo: {mensagem.anexo_nome}'


@login_required(login_url='entrar')
def conversas(request):
    _garantir_pedro(request.user)

    itens = []
    for conversa in request.user.conversas.all():
        ultima = conversa.mensagens.order_by('-criada_em', '-id').first()
        itens.append({
            'conversa': conversa,
            'previa': _previa(ultima),
            'hora': _hora_curta(ultima.criada_em) if ultima else '',
            'ordem': ultima.criada_em if ultima else conversa.criada_em,
        })
    # Quem mexeu por último aparece primeiro
    itens.sort(key=lambda i: i['ordem'], reverse=True)

    return render(request, 'core/conversas.html', {
        'itens': itens,
        'pode_criar': _eh_gerente(request.user),
    })


@login_required(login_url='entrar')
def nova_conversa(request):
    if not _eh_gerente(request.user):
        messages.error(request, "Só o gerente da empresa pode criar chats.")
        return redirect('conversas')

    empresa = _empresa_do_usuario(request.user)

    if request.method == 'POST':
        form = NovaConversaForm(
            request.POST, empresa=empresa, criador=request.user
        )
        if form.is_valid():
            with transaction.atomic():
                conversa = Conversa.objects.create(
                    tipo=Conversa.TIPO_GRUPO,
                    nome=form.cleaned_data['nome'].strip(),
                    empresa=empresa,
                    criador=request.user,
                )
                conversa.participantes.add(request.user)
                conversa.participantes.add(*form.cleaned_data['integrantes'])
            messages.success(request, "Chat criado!")
            return redirect('conversa_detalhe', pk=conversa.pk)
    else:
        form = NovaConversaForm(empresa=empresa, criador=request.user)

    return render(request, 'core/nova_conversa.html', {
        'form': form,
        'empresa': empresa,
        'sem_candidatos': not form.fields['integrantes'].queryset.exists(),
    })


def _salvar_mensagem(request, conversa):
    texto = request.POST.get('texto', '').strip()[:1000]
    arquivo = request.FILES.get('anexo')

    if not texto and not arquivo:
        return

    dados = {'conversa': conversa, 'autor': request.user, 'texto': texto}

    if arquivo:
        if arquivo.size > TAMANHO_MAX_ANEXO:
            messages.error(request, "O arquivo é maior que 10 MB.")
            return
        mime = (arquivo.content_type or '').split(';')[0].strip().lower()
        if mime.startswith('audio/'):
            tipo = 'audio'
        elif mime in IMAGENS_SEGURAS:
            tipo = 'imagem'
        else:
            tipo, mime = 'arquivo', 'application/octet-stream'
        dados.update(
            anexo=arquivo,
            anexo_nome=os.path.basename(arquivo.name)[:255],
            anexo_tipo=tipo,
            anexo_mime=mime,
        )

    Mensagem.objects.create(**dados)


@login_required(login_url='entrar')
def conversa_detalhe(request, pk):
    conversa = get_object_or_404(request.user.conversas, pk=pk)
    eh_pedro = conversa.tipo == Conversa.TIPO_PEDRO

    if request.method == 'POST':
        # O chat com o Pedro ainda não envia nada (será feito por outra pessoa)
        if not eh_pedro:
            _salvar_mensagem(request, conversa)
        return redirect('conversa_detalhe', pk=conversa.pk)

    mensagens = [
        {
            'obj': m,
            'minha': m.autor_id == request.user.id,
            'hora': timezone.localtime(m.criada_em).strftime('%H:%M'),
            # 3 cores de avatar, como no protótipo
            'cor': (m.autor_id or 0) % 3,
        }
        for m in conversa.mensagens.select_related('autor')
    ]

    return render(request, 'core/conversa.html', {
        'conversa': conversa,
        'eh_pedro': eh_pedro,
        'mensagens': mensagens,
        'total_integrantes': conversa.participantes.count(),
    })


@login_required(login_url='entrar')
def conversa_integrantes(request, pk):
    conversa = get_object_or_404(
        request.user.conversas, pk=pk, tipo=Conversa.TIPO_GRUPO
    )
    donos = set(conversa.empresa.donos.values_list('id', flat=True)) if conversa.empresa else set()

    integrantes = [
        {
            'nome': u.get_full_name() or u.username,
            'gerente': u.id in donos,
        }
        for u in conversa.participantes.order_by('first_name', 'username')
    ]

    return render(request, 'core/conversa_integrantes.html', {
        'conversa': conversa,
        'integrantes': integrantes,
        'voltar': reverse('conversa_detalhe', args=[conversa.pk]),
    })


@login_required(login_url='entrar')
def mensagem_anexo(request, pk):
    """Entrega o anexo só para quem participa da conversa."""
    mensagem = get_object_or_404(
        Mensagem.objects.filter(conversa__participantes=request.user), pk=pk
    )
    if not mensagem.anexo:
        raise Http404

    mime = mensagem.anexo_mime or 'application/octet-stream'

    try:
        arquivo = mensagem.anexo.open('rb')
    except FileNotFoundError:
        raise Http404

    if mensagem.anexo_tipo == 'audio':
        # Os navegadores (Safari principalmente) pedem o áudio em pedaços (Range)
        with arquivo:
            dados = arquivo.read()
        total = len(dados)
        inicio, fim, status = 0, total - 1, 200
        faixa = request.headers.get('Range', '')
        if faixa.startswith('bytes=') and total:
            try:
                a, b = faixa[6:].split(',')[0].split('-', 1)
                if a == '':
                    inicio = max(total - int(b), 0)
                else:
                    inicio = int(a)
                    fim = min(int(b), total - 1) if b else total - 1
                if inicio > fim or inicio >= total:
                    resposta = HttpResponse(status=416)
                    resposta['Content-Range'] = f'bytes */{total}'
                    return resposta
                status = 206
            except ValueError:
                inicio, fim, status = 0, total - 1, 200
        resposta = HttpResponse(dados[inicio:fim + 1], status=status, content_type=mime)
        resposta['Accept-Ranges'] = 'bytes'
        if status == 206:
            resposta['Content-Range'] = f'bytes {inicio}-{fim}/{total}'
    else:
        resposta = FileResponse(
            arquivo,
            content_type=mime,
            as_attachment=(mensagem.anexo_tipo != 'imagem'),
            filename=mensagem.anexo_nome or None,
        )

    resposta['X-Content-Type-Options'] = 'nosniff'
    resposta['Cache-Control'] = 'private, max-age=3600'
    return resposta


@login_required(login_url='entrar')
def excluir_documento(request, doc_id):
    empresa = request.user.empresas.first()
    documento = get_object_or_404(Documento, id=doc_id, empresa=empresa)
    documento.arquivo.delete(save=False)
    documento.delete()
    messages.success(request, "Documento removido do repositório.")
    return redirect('/perfil/?aba=documentos')


@login_required(login_url='entrar')
def remover_funcionario(request, func_id):
    empresa = request.user.empresas.first()
    funcionario = get_object_or_404(Funcionario, id=func_id, empresa=empresa)
    nome = funcionario.usuario.get_full_name() or funcionario.usuario.username
    funcionario.usuario.delete()
    messages.success(request, f"Acesso de {nome} removido da equipe.")
    return redirect('/perfil/?aba=funcionarios')


# ---------------------------------------------------------------------------
# PEDRO — assistente ESG (Gemini)
# ---------------------------------------------------------------------------

PEDRO_MAX_CARACTERES = 1000      # tamanho máximo de uma pergunta
PEDRO_MAX_HISTORICO = 20         # mensagens guardadas na sessão / enviadas ao Gemini
PEDRO_LIMITE_PERGUNTAS = 15      # perguntas por usuário...
PEDRO_JANELA_SEGUNDOS = 5 * 60   # ...a cada 5 minutos


@login_required(login_url='entrar')
def pedro_chat(request):
    # Pergunta vinda do card "Como posso ajudar hoje?" (enviada automaticamente)
    pergunta_inicial = request.GET.get('q', '').strip()[:PEDRO_MAX_CARACTERES]

    if hasattr(request.user, 'perfil_funcionario'):
        voltar = reverse('area_funcionario')
    else:
        voltar = reverse('home')

    return render(request, 'core/pedro_chat.html', {
        'historico': request.session.get('pedro_historico', []),
        'pergunta_inicial': pergunta_inicial,
        'voltar': voltar,
    })


@require_POST
def pedro_perguntar(request):
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Entre na sua conta para falar com o Pedro.'}, status=401)

    try:
        mensagem = json.loads(request.body or b'{}').get('mensagem', '')
    except (ValueError, AttributeError):
        mensagem = ''
    mensagem = str(mensagem).strip()

    if not mensagem:
        return JsonResponse({'erro': 'Escreva uma pergunta para o Pedro.'}, status=400)
    if len(mensagem) > PEDRO_MAX_CARACTERES:
        return JsonResponse(
            {'erro': f'Sua pergunta é muito longa (máximo de {PEDRO_MAX_CARACTERES} caracteres).'},
            status=400,
        )

    # Limite simples de perguntas para não estourar a cota do Gemini
    chave_limite = f'pedro_limite_{request.user.pk}'
    if cache.get(chave_limite, 0) >= PEDRO_LIMITE_PERGUNTAS:
        return JsonResponse(
            {'erro': 'Você fez muitas perguntas seguidas. Respire um pouco e tente de novo em alguns minutos. 🌱'},
            status=429,
        )
    cache.add(chave_limite, 0, PEDRO_JANELA_SEGUNDOS)
    cache.incr(chave_limite)

    historico = request.session.get('pedro_historico', [])
    agora = timezone.now().isoformat()
    pergunta = {'autor': 'usuario', 'texto': mensagem, 'hora': agora}

    try:
        resposta = pedro.perguntar(
            historico[-(PEDRO_MAX_HISTORICO - 1):] + [pergunta],
            pedro.montar_contexto(request.user),
        )
    except pedro.PedroIndisponivel as erro:
        return JsonResponse({'erro': str(erro)}, status=503)

    resposta_msg = {'autor': 'pedro', 'texto': resposta, 'hora': timezone.now().isoformat()}
    request.session['pedro_historico'] = (historico + [pergunta, resposta_msg])[-PEDRO_MAX_HISTORICO:]

    return JsonResponse({'resposta': resposta, 'hora': resposta_msg['hora']})


@require_POST
@login_required(login_url='entrar')
def pedro_limpar(request):
    request.session.pop('pedro_historico', None)
    return redirect('pedro_chat')