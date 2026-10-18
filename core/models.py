from django.db import models
from django.contrib.auth.models import User


class MensagemContato(models.Model):
    TIPO_CHOICES = [
        ('bug', 'Bug / Erro'),
        ('sugestao', 'Sugestão'),
        ('outros', 'Outros'),
    ]

    nome = models.CharField(max_length=100, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail")
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES, 
        default='sugestao', 
        verbose_name="Tipo"
    )
    mensagem = models.TextField(verbose_name="Mensagem")
    data_envio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Envio")

    class Meta:
        verbose_name = "Mensagem de Contato"
        verbose_name_plural = "Mensagens de Contato"
        ordering = ['-data_envio']

    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"


class Empresa(models.Model):
    # Relação com o Usuário e Contato
    donos = models.ManyToManyField(
        User, 
        related_name='empresas',
        verbose_name="Donos / Gestores"
    )
    telefone = models.CharField(
        max_length=20, 
        verbose_name="Telefone",
        blank=True, 
        null=True
    )

    # Opções para os campos de seleção
    PORTE_CHOICES = [
        ('micro', 'Microempresa'),
        ('pequena', 'Pequena Empresa'),
        ('media', 'Média Empresa'),
    ]

    FUNCIONARIOS_CHOICES = [
        ('1-9', 'Até 9 funcionários'),
        ('10-49', '10 a 49 funcionários'),
        ('50-99', '50 a 99 funcionários'),
        ('100+', '100 ou mais funcionários'),
    ]

    SEGMENTO_CHOICES = [
        ('restaurante', 'Restaurante'),
        ('lanchonete', 'Lanchonete / Fast Food'),
        ('padaria', 'Padaria / Confeitaria'),
        ('delivery', 'Apenas Delivery'),
        ('bar', 'Bar / Boteco'),
        ('outros', 'Outros do ramo alimentício'),
    ]

    # Perguntas Abertas
    nome_empresa = models.CharField(
        max_length=150,
        verbose_name="Nome da Empresa"
    )
    cidade_estado = models.CharField(
        max_length=100,
        verbose_name="Cidade - Estado"
    )

    # Dados da Empresa (Campos de Escolha)
    porte = models.CharField(
        max_length=20,
        choices=PORTE_CHOICES,
        default='micro',
        verbose_name="Porte da Empresa"
    )
    numero_funcionarios = models.CharField(
        max_length=20,
        choices=FUNCIONARIOS_CHOICES,
        default='1-9',
        verbose_name="Número de Funcionários"
    )
    segmento = models.CharField(
        max_length=50,
        choices=SEGMENTO_CHOICES,
        default='restaurante',
        verbose_name="Segmento da Empresa"
    )

    def __str__(self):
        return self.nome_empresa
    
    
    # BLOCO 3: QUESTIONÁRIO ESG ATUALIZADO (25 PERGUNTAS)

    # --- 🟢 Ações Baixas ---
    esg_01_higiene_manipulacao = models.BooleanField(
        default=False,
        verbose_name="Higiene e Manipulação Segura: Garantir que 100% da equipe siga as normas de higiene e controle de temperatura"
    )
    esg_02_separacao_lixo = models.BooleanField(
        default=False,
        verbose_name="Separação Simples de Lixo: Lixeiras separadas para recicláveis e orgânicos"
    )
    esg_03_coleta_oleo = models.BooleanField(
        default=False,
        verbose_name="Coleta de Óleo Usado: Armazenar e entregar para coletores locais habilitados"
    )
    esg_04_combate_desperdicio = models.BooleanField(
        default=False,
        verbose_name="Combate ao Desperdício Visível: Avisos no salão/buffet convidando a evitar sobras"
    )
    esg_05_cardapio_transparente = models.BooleanField(
        default=False,
        verbose_name="Cardápio Transparente: Sinalizar ingredientes, vegetarianos/veganos e alergênicos"
    )
    esg_06_recibos_digitais = models.BooleanField(
        default=False,
        verbose_name="Comandas e Recibos Digitais: Priorizar envio eletrônico para economizar papel"
    )
    esg_07_aeradores_torneiras = models.BooleanField(
        default=False,
        verbose_name="Aeradores nas Torneiras: Adaptadores para reduzir a vazão de água"
    )
    esg_08_organizacao_pvps = models.BooleanField(
        default=False,
        verbose_name="Organização PVPS no Estoque: Regra 'Primeiro que Vence, Primeiro que Sai'"
    )
    esg_09_descarte_lampadas_baterias = models.BooleanField(
        default=False,
        verbose_name="Descarte de Lâmpadas e Baterias: Pontos de coleta para lâmpadas e pilhas"
    )
    esg_10_caixa_sugestoes = models.BooleanField(
        default=False,
        verbose_name="Caixa de Sugestões/Denúncias: Canal simples para escutar a equipe"
    )
    esg_11_apagando_luz = models.BooleanField(
        default=False,
        verbose_name="Apagando LUZ: Desligar equipamentos e luzes em ambientes sem uso"
    )
    esg_12_uso_consciente_embalagens = models.BooleanField(
        default=False,
        verbose_name="Uso Consciente de Embalagens: Pergunta prévia sobre talheres e guardanapos extras no delivery"
    )

    # --- 🟡 Ações Médias (7 pontos cada) ---
    esg_13_doacao_excedente = models.BooleanField(
        default=False,
        verbose_name="Doação do Excedente Limpo: Doar alimentos não servidos seguros para ONGs ou abrigos"
    )
    esg_14_troca_descartaveis = models.BooleanField(
        default=False,
        verbose_name="Troca Gradual de Descartáveis: Substituir sacolas/embalagens por papel kraft ou biodegradáveis"
    )
    esg_15_apoio_anti_lesao = models.BooleanField(
        default=False,
        verbose_name="Compressas e Apoio Anti-Lesão: Pausas ativas e orientação postural para a equipe"
    )
    esg_16_compra_produtor_local = models.BooleanField(
        default=False,
        verbose_name="Compra na Feira/Produtor Local: Hortifrúti diretamente de pequenos produtores"
    )
    esg_17_planilha_perdas = models.BooleanField(
        default=False,
        verbose_name="Planilha de Perdas na Produção: Registrar descartes diários na pré-preparação"
    )
    esg_18_compostagem_basica = models.BooleanField(
        default=False,
        verbose_name="Compostagem Básica: Restos vegetais para hortas comunitárias ou composteiras"
    )
    esg_19_folga_aniversario_bem_estar = models.BooleanField(
        default=False,
        verbose_name="Folga de Aniversário ou Benefício Bem-Estar: Incentivos de saúde e folga festiva"
    )
    esg_20_treinamento_diversidade = models.BooleanField(
        default=False,
        verbose_name="Treinamento Sobre Diversidade: Orientação para respeito e atendimento inclusivo"
    )

    # --- 🔴 Ações Altas (6 pontos cada) ---
    esg_21_ovos_cage_free_compra_etica = models.BooleanField(
        default=False,
        verbose_name="Ovos Cage-Free e Compra Ética: Ovos de galinhas livres de gaiola e carnes auditadas"
    )
    esg_22_equipamentos_inverter = models.BooleanField(
        default=False,
        verbose_name="Equipamentos Inverter/Eficientes: Refrigeração/ar-condicionado Procel A / Inverter"
    )
    esg_23_opcoes_plant_based = models.BooleanField(
        default=False,
        verbose_name="Opções Plant-Based no Cardápio: Pratos 100% à base de plantas no menu"
    )
    esg_24_selo_certificacao_local = models.BooleanField(
        default=False,
        verbose_name="Selo ou Certificação Local: Certificação municipal de sustentabilidade ou Lixo Zero"
    )
    esg_25_energia_solar = models.BooleanField(
        default=False,
        verbose_name="Uso de Energia Solar: Cooperativas de energia solar ou geração própria 100% limpa"
    )