import os
from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask import make_response
import csv
from io import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm, mm
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


translations = {
    "Calculadora de Emissões de CO₂ em Deslocamentos para Eventos Náuticos": "CO₂ Emissions Calculator for Travel to Nautical Events",
    "Faça a diferença pelo planeta": "Make a difference for the planet",
    "Ao preencher o questionário, nossa calculadora conseguirá estimar suas emissões de carbono nos deslocamentos": "By filling out the questionnaire, our calculator will be able to estimate your carbon emissions from travel",
    "Iniciar Questionário": "Start Questionnaire",
    "Por que calcular?": "Why calculate?",
    "O transporte é responsável por cerca de 24% das emissões globais de CO2. Suas escolhas fazem diferença!": "Transport is responsible for about 24% of global CO2 emissions. Your choices make a difference!",
    "Como funciona?": "How does it work?",
    "Responda algumas perguntas sobre seus deslocamentos e veja gráficos em tempo real": "Answer a few questions about your travel and see real-time graphs",
    "Participe da mudança": "Take part in the change",
    "Seus dados ajudam a entender padrões e promover eventos mais sustentáveis": "Your data helps understand patterns and promote more sustainable events",
    "Uma iniciativa da parceria entre CBVela e ETTA/UFF com o apoio do CNPq e Faperj para promover a conscientização ambiental em eventos esportivos": "An initiative of the partnership between CBVela and ETTA/UFF with the support of CNPq and Faperj to promote environmental awareness in sports events",


    "Questionário de Emissões de CO₂": "CO₂ Emissions Questionnaire",
    "Preencha os dados abaixo para calcular o impacto ambiental do seu deslocamento.": "Fill in the data below to calculate the environmental impact of your travel.",
    "Email": "Email",
    "País de origem": "Country of origin",
    "Tipo de participante": "Participant type",
    "Transporte usado para chegar à cidade do evento": "Transport used to arrive at the event city",
    "Distância percorrida (km)": "Distance traveled (km)",
    "Custo com transporte (R$, opcional)": "Transport cost (R$, optional)",
    "Transporte usado no dia a dia do evento": "Transport used daily during the event",
    "Distância percorrida por dia (km)": "Distance traveled per day (km)",
    "Número de dias de participação": "Number of days of participation",
    "Custo com transporte diário (R$, opcional)": "Daily transport cost (R$, optional)",
    "Gasto com alimentação (R$)": "Food expenses (R$)",
    "Gasto com transporte de equipamentos (R$)": "Equipment transport expenses (R$)",
    "Gasto com aluguel de botes (R$)": "Boat rental expenses (R$)",
    "Gasto com hospedagem (R$)": "Accommodation expenses (R$)",
    "Pontos turísticos visitados (opcional)": "Tourist attractions visited (optional)",
    "Calcular Emissões": "Calculate Emissions",
    "Seus Resultados de Emissão de CO₂": "Your CO₂ Emission Results",
    "Dados do Participante": "Participant Data",
    "Emissão total estimada": "Estimated total emission",
    "Detalhamento": "Breakdown",
    "Transporte até a cidade:": "Transport to the city:",
    "Transporte local (por dia):": "Local transport (per day):",
    "Análise do Evento": "Event Analysis",
    "Baixar Relatório em PDF": "Download PDF Report",
    "Responder novamente": "Answer again",
    "Página inicial": "Home page",
    "Obrigado por contribuir com a sustentabilidade dos eventos náuticos!": "Thank you for contributing to the sustainability of nautical events!",
    "← Voltar para a página inicial": "← Back to home page",


    "Resultados da sua Emissão de CO2": "Your CO2 Emission Results",
    "Veja o impacto ambiental dos seus deslocamentos": "See the environmental impact of your travel",
    "Resumo da Sua Emissão": "Your Emission Summary",
    "Total de emissões de carbono": "Total carbon emissions",
    "Detalhes:": "Details:",
    "Local de Origem:": "Place of Origin:",
    "Estrangeiro": "Foreign",
    "Tipo:": "Type:",
    "Transporte até a cidade:": "Transport to the city:",
    "Transporte local:": "Local transport:",
    "Dias de evento:": "Event days:",
    "Data:": "Date:",
    "O que isso significa?": "What does this mean?",
    "Sua emissão de": "Your emission of",
    "equivale a:": "is equivalent to:",
    "árvores absorvendo CO2 por um ano": "trees absorbing CO2 for one year",
    "Estatísticas Coletivas": "Collective Statistics",
    "Gráficos atualizados com todas as respostas recebidas:": "Charts updated with all received answers:",
    "Dicas para Reduzir Sua Emissão:": "Tips to Reduce Your Emission:",
    "Prefira transportes públicos sempre que possível": "Prefer public transport whenever possible",
    "Considere a carona solidária para eventos": "Consider ride sharing for events",
    "Para distâncias curtas, use bicicleta ou caminhe": "For short distances, use a bicycle or walk",
    "Compense suas emissões com programas de reflorestamento": "Offset your emissions with reforestation programs",
    "Realizar Novo Cálculo": "Perform New Calculation",
    "Página Inicial": "Home Page",
    "Baixar Informações PDF": "Download PDF Information",
    "Juntos podemos promover eventos esportivos mais sustentáveis!": "Together we can promote more sustainable sports events!",

    "Selecione seu estado de origem": "--Select your state of origin",
    "Selecione seu tipo de participação": "--Select your participant type",
    "Selecione o transporte utilizado": "--Select the transport used",
    "Principal meio de transporte utilizado:": "Main means of transport used:",

    # ========== TIPOS DE TRANSPORTE ==========
    "Carro": "--Car",
    "Ônibus": "--Bus",
    "Avião": "--Plane",
    "Barca": "--Ferry",
    "Bicicleta/a pé": "--Bicycle/Walking",
    "Moto": "--Motorcycle",
    "Trem": "--Train",
    "Outros": "--Other",
    
    # ========== TIPOS DE PARTICIPANTE ==========
    "Velejador(a)": "--Sailor",
    "Técnico/Técnica": "--Coach",
    "Acompanhante do atleta": "--Athlete Guest ",
    "Comissão de regata": "--Race Committee",
    "Prestador/Prestadora de serviço": "--Service provider",
    "Organização": "--Staff",
    "Outro": "--Other",



    "País de Origem:": "Country of Origin:",
    "Selecione seu país de origem": " --Select your country of origin",
    "País": "Country",
    "País de Origem": "Country of Origin",
    "Estrangeiro": "International",


    "Tipo de Deslocamento": "Trip Type",
    "Transporte": "Transport",
    "Distância": "Distance",
    "Emissão (kgCO2e)": "Emissions (kgCO2e)",
    "Até a cidade do evento": "To the event city",
    "Deslocamento local": "Local commute",
    "TOTAL": "TOTAL",
    

    "Equivalência": "Equivalence",
    "Valor Aproximado": "Approximate Value",
    "Árvores para absorver em 1 ano": "Trees to absorb in 1 year",
    "Horas de lâmpada LED (60W)": "Hours of LED bulb (60W)",
    "Emissão diária média brasileira*": "Average daily Brazilian emission*",
    "árvores": "trees",
    "horas": "hours",


        "Local de Origem:": "Place of Origin:",
    "Tipo de Participante:": "Participant Type:",
    "Email:": "Email:",
    "Estrangeiro": "International",
    
    # Recomendações
    "🏨 Escolha acomodações próximas ao local do evento, reduzindo a necessidade de transporte motorizado": 
        "🏨 Choose accommodations close to the event venue, reducing the need for motorized transport",
    "🚶 Para distâncias curtas, opte por caminhar ou pedalar, formas ativas e sustentáveis de locomoção que também favorecem a saúde e o bem-estar": 
        "🚶 For short distances, choose walking or cycling, active and sustainable forms of mobility that also promote health and well-being",
    "🌱 Prefira transportes públicos ou coletivos para deslocamentos sempre que possível": 
        "🌱 Prefer public or collective transportation whenever possible",
    "🚗 Organize caronas solidárias com outros participantes, otimizando o uso dos veículos e diminuindo o número de deslocamentos individuais": 
        "🚗 Organize carpooling with other participants, optimizing vehicle use and reducing the number of individual trips",
    "📅 Planeje seus deslocamentos com antecedência para evitar horários de tráfego intenso e, consequentemente, o aumento do consumo de combustível": 
        "📅 Plan your trips in advance to avoid peak traffic times and consequently reduce fuel consumption",
    "💡 Dê preferência a veículos elétricos ou híbridos, quando disponíveis, para minimizar o impacto ambiental dos deslocamentos": 
        "💡 Prefer electric or hybrid vehicles when available to minimize the environmental impact of travel",
    "🌳 Compense emissões participando de programas de reflorestamento ou outras iniciativas ambientais reconhecidas": 
        "🌳 Compensate emissions by participating in reforestation programs or other recognized environmental initiatives"
}




database_url = os.environ.get('DATABASE_URL')
if database_url:
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"✅ Usando PostgreSQL: {database_url.split('@')[1] if '@' in database_url else database_url}")
else:
    # DESENVOLVIMENTO (Local) - Tenta .env, depois fallback para SQLite
    try:
        from dotenv import load_dotenv
        load_dotenv()
        env_db_url = os.environ.get('DATABASE_URL')
        if env_db_url:
            app.config['SQLALCHEMY_DATABASE_URI'] = env_db_url
            print("✅ .env carregado com sucesso")
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calculadora_co2.db'
            print("✅ Usando SQLite (fallback)")
    except Exception as e:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calculadora_co2.db'
        print(f"⚠️  Erro .env: {e}, usando SQLite")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class RespostaEmissao(db.Model):
    __tablename__ = 'respostas_emissao'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    pais_origem_pt = db.Column(db.String(100), nullable=False)
    pais_origem_en = db.Column(db.String(100), nullable=False)
  #  estado_origem = db.Column(db.String(100), nullable=False)
    tipo_participante = db.Column(db.String(50), nullable=False)
    transporte_cidade = db.Column(db.String(50), nullable=False)
    distancia_cidade = db.Column(db.Numeric(10, 2), nullable=False)
    custo_transporte = db.Column(db.Numeric(10, 2), nullable=True) 
    transporte_local = db.Column(db.String(50), nullable=False)
    distancia_local = db.Column(db.Numeric(10, 2), nullable=False)
    dias_evento = db.Column(db.Integer, nullable=False)
    custo_transporte_diario = db.Column(db.Numeric(10, 2), nullable=True)

    gasto_alimentacao = db.Column(db.Numeric(10, 2), nullable=True)      
    gasto_equipamentos = db.Column(db.Numeric(10, 2), nullable=True)    
    gasto_botes = db.Column(db.Numeric(10, 2), nullable=True)            
    gasto_hospedagem = db.Column(db.Numeric(10, 2), nullable=True)       

    
    pontos_turisticos = db.Column(db.Text, nullable=True)          

    emissao_total = db.Column(db.Numeric(10, 2), nullable=False)
    #created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
#           'estado_origem': self.estado_origem,
            'pais_origem_pt': self.pais_origem_pt,
            'pais_origem_en': self.pais_origem_en,
            'tipo_participante': self.tipo_participante,
            'transporte_cidade': self.transporte_cidade,
            'distancia_cidade': float(self.distancia_cidade),
            'custo_transporte': float(self.custo_transporte) if self.custo_transporte else None,
            'transporte_local': self.transporte_local,
            'distancia_local': float(self.distancia_local),
            'dias_evento': self.dias_evento,
            'custo_transporte_diario': float(self.custo_transporte_diario) if self.custo_transporte_diario else None,
            
            # Logisticas do evento
            'gasto_alimentacao': float(self.gasto_alimentacao) if self.gasto_alimentacao else None,
            'gasto_equipamentos': float(self.gasto_equipamentos) if self.gasto_equipamentos else None,
            'gasto_botes': float(self.gasto_botes) if self.gasto_botes else None,
            'gasto_hospedagem': float(self.gasto_hospedagem) if self.gasto_hospedagem else None,
            'pontos_turisticos': self.pontos_turisticos,

            'emissao_total': float(self.emissao_total),
        }

# Dados de emissão por transporte (gCO2/km)
EMISSOES_TRANSPORTE = {
    "carro": 97.8,
    "ônibus": 67,
    "avião": 42,
    "barca": 60.3,
    "bicicleta/a pé": 0,
    "moto": 80.5,
    "trem": 20.9,
    "outros": 50
}

# Lista de tipos de participantes
TIPOS_PARTICIPANTE = [
    "Velejador(a)",
    "Técnico/Técnica",
    "Acompanhante do atleta", 
    "Comissão de regata",
    "Prestador/Prestadora de serviço",
    "Organização",
    "Outro"
]

# Lista de estados brasileiros + opção para estrangeiros
ESTADOS_BRASIL = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", 
    "Distrito Federal", "Espírito Santo", "Goiás", "Maranhão", 
    "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará", 
    "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro", 
    "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", "Roraima", 
    "Santa Catarina", "São Paulo", "Sergipe", "Tocantins",
    "Não se aplica (estrangeiro)"
]


# Listas de países (português e inglês)
PAISES_PORTUGUES = [
    "Afeganistão", "África do Sul", "Albânia", "Alemanha", "Andorra", "Angola", 
    "Antígua e Barbuda", "Arábia Saudita", "Argélia", "Argentina", "Armênia", 
    "Austrália", "Áustria", "Azerbaijão", "Bahamas", "Bahrein", "Bangladesh", 
    "Barbados", "Bélgica", "Belize", "Benim", "Bielorrússia", "Bolívia", 
    "Bósnia e Herzegovina", "Botsuana", "Brasil", "Brunei", "Bulgária", 
    "Burkina Faso", "Burundi", "Butão", "Cabo Verde", "Camarões", "Camboja", 
    "Canadá", "Catar", "Cazaquistão", "Chade", "Chile", "China", "Chipre", 
    "Colômbia", "Comores", "Congo (Congo-Brazzaville)", "Coreia do Norte", 
    "Coreia do Sul", "Costa do Marfim", "Costa Rica", "Croácia", "Cuba", 
    "Dinamarca", "Djibouti", "Dominica", "Egito", "El Salvador", 
    "Emirados Árabes Unidos", "Equador", "Eritreia", "Eslováquia", "Eslovênia", 
    "Espanha", "Essuatíni", "Estados Unidos", "Estônia", "Etiópia", "Fiji", 
    "Filipinas", "Finlândia", "França", "Gabão", "Gâmbia", "Gana", "Geórgia", 
    "Granada", "Grécia", "Guatemala", "Guiana", "Guiné", "Guiné Equatorial", 
    "Guiné-Bissau", "Haiti", "Holanda (Países Baixos)", "Honduras", "Hungria", 
    "Iêmen", "Ilhas Marshall", "Ilhas Salomão", "Índia", "Indonésia", "Irã", 
    "Iraque", "Irlanda", "Islândia", "Israel", "Itália", "Jamaica", "Japão", 
    "Jordânia", "Kiribati", "Kuwait", "Laos", "Lesoto", "Letônia", "Líbano", 
    "Libéria", "Líbia", "Liechtenstein", "Lituânia", "Luxemburgo", 
    "Macedônia do Norte", "Madagascar", "Malásia", "Malawi", "Maldivas", "Mali", 
    "Malta", "Marrocos", "Maurício", "Mauritânia", "México", "Micronésia", 
    "Moçambique", "Moldávia", "Mônaco", "Mongólia", "Montenegro", 
    "Myanmar (Birmânia)", "Namíbia", "Nauru", "Nepal", "Nicarágua", "Níger", 
    "Nigéria", "Noruega", "Nova Zelândia", "Omã", "Palau", "Palestina (Estado da)", 
    "Panamá", "Papua-Nova Guiné", "Paquistão", "Paraguai", "Peru", "Polônia", 
    "Portugal", "Quênia", "Quirguistão", "Reino Unido", "República Centro-Africana", 
    "República Democrática do Congo", "República Dominicana", "República Tcheca", 
    "Romênia", "Ruanda", "Rússia", "Samoa", "Santa Lúcia", "São Cristóvão e Névis", 
    "São Marinho", "São Tomé e Príncipe", "São Vicente e Granadinas", "Seicheles", 
    "Senegal", "Serra Leoa", "Sérvia", "Singapura", "Síria", "Somália", "Sri Lanka", 
    "Sudão", "Sudão do Sul", "Suécia", "Suíça", "Suriname", "Tailândia", 
    "Tajiquistão", "Tanzânia", "Timor-Leste", "Togo", "Tonga", "Trinidad e Tobago", 
    "Tunísia", "Turcomenistão", "Turquia", "Tuvalu", "Ucrânia", "Uganda", 
    "Uruguai", "Uzbequistão", "Vanuatu", "Vaticano (Santa Sé)", "Venezuela", 
    "Vietnã", "Zâmbia", "Zimbábue"
]

PAISES_INGLES = [
"--Afghanistan", "--South Africa", "--Albania", "--Germany", "--Andorra", "--Angola", "--Antigua and Barbuda", 
"--Saudi Arabia", "--Algeria", "--Argentina", "--Armenia", "--Australia", "--Austria", "--Azerbaijan", "--Bahamas", 
"--Bahrain", "--Bangladesh", "--Barbados", "--Belgium", "--Belize", "--Benin", "--Belarus", "--Bolivia",
 "--Bosnia and Herzegovina", "--Botswana", "--Brazil", "--Brunei", "--Bulgaria", "--Burkina Faso", "--Burundi",
   "--Bhutan", "--Cabo Verde", "--Cameroon", "--Cambodia", "--Canada", "--Qatar", "--Kazakhstan", "--Chad", "--Chile",
 "--China", "--Cyprus", "--Colombia", "--Comoros", "--Congo (Congo-Brazzaville)", "--North Korea", "--South Korea",
"--Côte d'Ivoire", "--Costa Rica", "--Croatia", "--Cuba", "--Denmark", "--Djibouti", "--Dominica", "--Egypt", "--El Salvador",
"--United Arab Emirates", "--Ecuador", "--Eritrea", "--Slovakia", "--Slovenia", "--Spain", "--Eswatini", "--United States", 
"--Estonia", "--Ethiopia", "--Fiji", "--Philippines", "--Finland", "--France", "--Gabon", "--Gambia", "--Ghana", "--Georgia", 
"--Grenada", "--Greece", "--Guatemala", "--Guyana", "--Guinea", "--Equatorial Guinea", "--Guinea-Bissau", "--Haiti", 
"--Netherlands", "--Honduras", "--Hungary", "--Yemen", "--Marshall Islands", "--Solomon Islands", "--India", "--Indonesia", 
"--Iran", "--Iraq", "--Ireland", "--Iceland", "--Israel", "--Italy", "--Jamaica", "--Japan", "--Jordan", "--Kiribati", 
"--Kuwait", "--Laos", "--Lesotho", "--Latvia", "--Lebanon", "--Liberia", "--Libya", "--Liechtenstein", "--Lithuania", 
"--Luxembourg", "--North Macedonia", "--Madagascar", "--Malaysia", "--Malawi", "--Maldives", "--Mali", "--Malta", "--Morocco", 
"--Mauritius", "--Mauritania", "--Mexico", "--Micronesia", "--Mozambique", "--Moldova", "--Monaco", "--Mongolia", 
"--Montenegro", "--Myanmar (Burma)", "--Namibia", "--Nauru", "--Nepal", "--Nicaragua", "--Niger", "--Nigeria", "--Norway", 
"--New Zealand", "--Oman", "--Palau", "--Palestine (State of)", "--Panama", "--Papua New Guinea", "--Pakistan", "--Paraguay", 
"--Peru", "--Poland", "--Portugal", "--Kenya", "--Kyrgyzstan", "--United Kingdom", "--Central African Republic", 
"--Democratic Republic of the Congo", "--Dominican Republic", "--Czechia (Czech Republic)", "--Romania", "--Rwanda", "--Russia", 
"--Samoa", "--Saint Lucia", "--Saint Kitts and Nevis", "--San Marino", "--Sao Tome and Principe", 
"--Saint Vincent and the Grenadines", "--Seychelles", "--Senegal", "--Sierra Leone", "--Serbia", "--Singapore", "--Syria", 
"--Somalia", "--Sri Lanka", "--Sudan", "--South Sudan", "--Sweden", "--Switzerland", "--Suriname", "--Thailand", "--Tajikistan", 
"--Tanzania", "--Timor-Leste", "--Togo", "--Tonga", "--Trinidad and Tobago", "--Tunisia", "--Turkmenistan", "--Turkey", 
"--Tuvalu", "--Ukraine", "--Uganda", "--Uruguay", "--Uzbequistão", "--Vanuatu", "--Holy See (Vatican City)", "--Venezuela", 
"--Vietnam", "--Zambia", "--Zimbabwe"
]

PAISES_DICT = dict(zip(PAISES_PORTUGUES, PAISES_INGLES))

for pt, en in PAISES_DICT.items():
    translations[pt] = en







def gerar_grafico_base64():
    """Gera 4 gráficos: transportes (chegada/diário), emissões por transporte e econômico"""
    try:
        with app.app_context():
            respostas = RespostaEmissao.query.all()
        
        if not respostas:
            return None
        
        # ===== PREPARAÇÃO DOS DADOS =====
        transporte_chegada = {}
        transporte_diario = {}
        
        emissoes_transporte = {transp: 0 for transp in EMISSOES_TRANSPORTE.keys()}
        
        # Acumuladores para dados econômicos
        gastos = {
            'alimentacao': 0,
            'equipamentos': 0,
            'botes': 0,
            'hospedagem': 0,
            'transporte_chegada': 0,
            'transporte_diario': 0
        }
        
        total_respostas = len(respostas)
        
        for resposta in respostas:
            # Contagem de transportes (chegada)
            transp_chegada = resposta.transporte_cidade
            transporte_chegada[transp_chegada] = transporte_chegada.get(transp_chegada, 0) + 1
            
            # Contagem de transportes (diário)
            transp_diario = resposta.transporte_local
            transporte_diario[transp_diario] = transporte_diario.get(transp_diario, 0) + 1
            
            # Emissões por tipo de transporte (usando o transporte de chegada)
            if transp_chegada in emissoes_transporte:
                emissoes_transporte[transp_chegada] += float(resposta.emissao_total)
            
            # Acumular gastos econômicos
            if resposta.custo_transporte:
                # 🚗 Transporte de Chegada: multiplicado por 1.5
                gastos['transporte_chegada'] += float(resposta.custo_transporte)
            if resposta.custo_transporte_diario:
                gastos['transporte_diario'] += float(resposta.custo_transporte_diario)*1.5
            if resposta.gasto_alimentacao:
                gastos['alimentacao'] += float(resposta.gasto_alimentacao)*1.5
            if resposta.gasto_equipamentos:
                gastos['equipamentos'] += float(resposta.gasto_equipamentos)*1.5
            if resposta.gasto_botes:
                gastos['botes'] += float(resposta.gasto_botes)*1.5
            if hasattr(resposta, 'gasto_hospedagem') and resposta.gasto_hospedagem:
                gastos['hospedagem'] += float(resposta.gasto_hospedagem)*1.5
        
        # ===== CRIAÇÃO DOS GRÁFICOS =====
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Análise de Sustentabilidade e Impacto Econômico - Regata', 
                    fontsize=16, fontweight='bold', y=0.98, color='#1a3b5d')
        
        # Palheta de cores personalizada: azul, verde e amarelo
        palheta_cores = ["#1CE074", "#0B9A5F", "#026C26", "#27A8DC", "#2775E2", "#054976"]
        
        # ===== GRÁFICO 1: Transporte para CHEGAR =====
        if transporte_chegada:
            transportes_ord = sorted(transporte_chegada.items(), key=lambda x: x[1], reverse=True)
            labels = [f"{t[0].capitalize()}" for t in transportes_ord]
            valores = [t[1] for t in transportes_ord]
            
            cores_barras = [palheta_cores[i % len(palheta_cores)] for i in range(len(valores))]
            
            bars = ax1.bar(range(len(valores)), valores, color=cores_barras, 
                          edgecolor='#2c3e50', linewidth=1.5, alpha=0.9)
            ax1.set_xticks(range(len(valores)))
            ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=9, fontweight='500')
            
            for bar, valor in zip(bars, valores):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{valor}', ha='center', va='bottom', fontsize=10, 
                        fontweight='bold', color='#1a3b5d')
            
            ax1.set_title('Transporte mais utilizado para CHEGAR ao evento', 
                         fontsize=12, fontweight='bold', pad=15, color='#1a3b5d')
            ax1.set_ylabel('Número de participantes', fontsize=10, fontweight='500', color='#2c3e50')
            ax1.grid(axis='y', alpha=0.2, linestyle='--', color='#95a5a6')
            from matplotlib.ticker import MaxNLocator
            ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
            
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
        
        # ===== GRÁFICO 2: Transporte no DIA A DIA =====
        if transporte_diario:
            transportes_ord = sorted(transporte_diario.items(), key=lambda x: x[1], reverse=True)
            labels = [f"{t[0].capitalize()}" for t in transportes_ord]
            valores = [t[1] for t in transportes_ord]
            
            cores_barras = [palheta_cores[(i+2) % len(palheta_cores)] for i in range(len(valores))]
            
            bars = ax2.bar(range(len(valores)), valores, color=cores_barras,
                          edgecolor='#2c3e50', linewidth=1.5, alpha=0.9)
            ax2.set_xticks(range(len(valores)))
            ax2.set_xticklabels(labels, rotation=45, ha='right', fontsize=9, fontweight='500')
            
            for bar, valor in zip(bars, valores):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{valor}', ha='center', va='bottom', fontsize=10,
                        fontweight='bold', color='#1a3b5d')
            
            ax2.set_title('Transporte mais utilizado no DIA A DIA do evento', 
                         fontsize=12, fontweight='bold', pad=15, color='#1a3b5d')
            ax2.set_ylabel('Número de participantes', fontsize=10, fontweight='500', color='#2c3e50')
            ax2.grid(axis='y', alpha=0.2, linestyle='--', color='#95a5a6')
            ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
            
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
        
        # ===== GRÁFICO 3: Distribuição de Emissões por Tipo de Transporte (PIZZA TRADICIONAL) =====
        if any(emissoes_transporte.values()):
            transportes_validos = {k: v for k, v in emissoes_transporte.items() if v > 0}
            
            if transportes_validos:
                labels = [k.capitalize() for k in transportes_validos.keys()]
                valores = list(transportes_validos.values())
                total_emissoes = sum(valores)
                
                dados_ordenados = sorted(zip(labels, valores), key=lambda x: x[1], reverse=True)
                labels = [d[0] for d in dados_ordenados]
                valores = [d[1] for d in dados_ordenados]
                
                percentuais = [(v/total_emissoes)*100 for v in valores]
                
                cores_pizza = [palheta_cores[i % len(palheta_cores)] for i in range(len(valores))]
                
                explode = [0.03 if v == max(valores) else 0 for v in valores]
                
                wedges, texts, autotexts = ax3.pie(
                    valores, 
                    labels=labels, 
                    autopct=lambda pct: f'{pct:.1f}%\n({(pct/100)*total_emissoes:,.0f} kg)',
                    colors=cores_pizza,
                    explode=explode,
                    shadow=True,
                    startangle=90,
                    textprops={'fontsize': 8}
                )
                
                # Formatação dos textos
                for text in texts:
                    text.set_fontsize(9)
                    text.set_fontweight('500')
                    text.set_color('#2c3e50')
                
                for autotext in autotexts:
                    autotext.set_fontsize(7)
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_bbox(dict(facecolor='#2c3e50', alpha=0.6, 
                                          edgecolor='none', pad=1.5))
                
                ax3.set_title(f'Distribuição de Emissões por Tipo de Transporte\nTotal: {total_emissoes:,.0f} kgCO₂', 
                             fontsize=12, fontweight='bold', pad=15, color='#1a3b5d')
        
        # ===== GRÁFICO 4: Distribuição Econômica por Categoria =====
        if any(gastos.values()):
            categorias_validas = {k: v for k, v in gastos.items() if v > 0}
            
            if categorias_validas:
                nomes_categorias = {
                    'alimentacao': 'Alimentação',
                    'equipamentos': 'Equipamentos',
                    'botes': 'Aluguel de Botes',
                    'hospedagem': 'Hospedagem',
                    'transporte_chegada': 'Transporte (Chegada)',
                    'transporte_diario': 'Transporte (Diário)'
                }
                
                labels = [nomes_categorias[k] for k in categorias_validas.keys()]
                valores = list(categorias_validas.values())
                total_gastos = sum(valores)
                
                dados_ordenados = sorted(zip(labels, valores), key=lambda x: x[1], reverse=True)
                labels = [d[0] for d in dados_ordenados]
                valores = [d[1] for d in dados_ordenados]
                
                cores_pizza = [palheta_cores[(i+3) % len(palheta_cores)] for i in range(len(valores))]
                
                explode = [0.05 if v == max(valores) else 0 for v in valores]
                
                wedges, texts, autotexts = ax4.pie(
                    valores, 
                    labels=labels, 
                    autopct=lambda pct: f'R$ {(pct/100)*total_gastos:,.0f}',
                    colors=cores_pizza,
                    explode=explode,
                    shadow=True,
                    startangle=90,
                    textprops={'fontsize': 8}
                )
                
                for text in texts:
                    text.set_fontsize(9)
                    text.set_fontweight('500')
                    text.set_color('#2c3e50')
                
                for autotext in autotexts:
                    autotext.set_fontsize(8)
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_bbox(dict(facecolor='#2c3e50', alpha=0.5, 
                                          edgecolor='none', pad=1))
                
                ax4.set_title(f'Distribuição Econômica por Categoria\nTotal: R$ {total_gastos:,.2f}', 
                             fontsize=12, fontweight='bold', pad=15, color='#1a3b5d')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100, 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
        
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
        import traceback
        traceback.print_exc()
        return None



def emoji_para_imagem(emoji, tamanho=12):
    """Converte emoji em imagem base64"""
    try:
        fig, ax = plt.subplots(figsize=(tamanho/24, tamanho/24))
        ax.text(0.5, 0.5, emoji, fontsize=tamanho, ha='center', va='center')
        ax.axis('off')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', 
                   pad_inches=0, transparent=True, dpi=100)
        buffer.seek(0)
        plt.close()
        
        return ImageReader(buffer)
    except:
        return None

def criar_linha_com_emoji(emoji, texto, estilo, tamanho_emoji=12):
    """Cria uma linha com emoji como imagem"""
    try:
        img_emoji = emoji_para_imagem(emoji, tamanho_emoji)
        if img_emoji:
            img_obj = Image(img_emoji, width=4*mm, height=4*mm)
            
            dados_linha = [
                [img_obj, Paragraph(texto, estilo)]
            ]
            tabela = Table(dados_linha, colWidths=[6*mm, 150*mm])
            tabela.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 2),
                ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            return tabela
        else:
            return Paragraph(f"• {texto}", estilo)
    except Exception as e:
        print(f"Erro ao criar linha com emoji: {e}")
        return Paragraph(f"• {texto}", estilo)

def gerar_pdf(registro):
    """Gera PDF com os resultados do questionário - TABELAS SEPARADAS PT/EN"""
    try:
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=72, 
            leftMargin=72,
            topMargin=72, 
            bottomMargin=18,
            title=f"Emissão CO2e - {registro['email']} | CO2e Emissions - {registro['email']}"
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # ===== ESTILOS PERSONALIZADOS =====
        estilo_titulo = ParagraphStyle(
            'TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=15,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1
        )
        
        estilo_titulo_en = ParagraphStyle(
            'TituloIngles',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            alignment=1,
            fontName='Helvetica-Oblique'
        )
        
        estilo_subtitulo = ParagraphStyle(
            'Subtitulo',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.HexColor('#34495e')
        )
        
        estilo_subtitulo_en = ParagraphStyle(
            'SubtituloIngles',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            spaceAfter=10,
            fontName='Helvetica-Oblique'
        )
        
        estilo_normal = ParagraphStyle(
            'NormalCustom',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        estilo_normal_en = ParagraphStyle(
            'NormalIngles',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            spaceAfter=8,
            fontName='Helvetica-Oblique'
        )
        
        estilo_destaque = ParagraphStyle(
            'Destaque',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#27ae60'),
            alignment=1,
            spaceAfter=15
        )
        
        estilo_destaque_en = ParagraphStyle(
            'DestaqueIngles',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=1,
            spaceAfter=20,
            fontName='Helvetica-Oblique'
        )

        # ===== CABEÇALHO BILINGUE =====
        titulo_pt = "Cada Deslocamento Conta: Seu Impacto em CO2e no Evento"
        titulo_en = translations.get(titulo_pt, "Every Trip Counts: Your CO2e Impact at the Event")        
        elements.append(Paragraph(titulo_pt, estilo_titulo))
        elements.append(Paragraph(titulo_en, estilo_titulo_en))
        elements.append(Spacer(1, 15))
        # Linha divisória
        linha_divisoria = Table([[""]], colWidths=[16*cm], rowHeights=[1])
        linha_divisoria.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#3498db')),
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#3498db')),
        ]))
        elements.append(linha_divisoria)
        elements.append(Spacer(1, 20))

        # ===== DADOS DO PARTICIPANTE - SEPARADO PT/EN =====
        
        elements.append(Paragraph("DADOS DO PARTICIPANTE", estilo_subtitulo))
        
        tipo_traduzido = translations.get(registro['tipo_participante'])

        
        # TABELA EM PORTUGUÊS
        dados_pessoais_pt = [
            ["País de Origem:", registro['pais_origem_pt']],  # Nova linha
            ["Tipo de Participante:", registro['tipo_participante']],
            ["Email:", registro['email']],
        ]
        
        tabela_dados_pt = Table(dados_pessoais_pt, colWidths=[4*cm, 10*cm])
        tabela_dados_pt.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica', 10),
            ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#bdc3c7')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        
        elements.append(tabela_dados_pt)
        elements.append(Spacer(1, 10))
        
        # TÍTULO INGLÊS
        elements.append(Paragraph("PARTICIPANT DATA", estilo_subtitulo_en))
        
        # TABELA EM INGLÊS
        dados_pessoais_en = [
            ["Country of Origin:", registro['pais_origem_en']],
            ["Participant Type:", tipo_traduzido],
            ["Email:", registro['email']],
        ]
        
        tabela_dados_en = Table(dados_pessoais_en, colWidths=[4*cm, 10*cm])
        tabela_dados_en.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica-Oblique', 9),
            ('FONT', (0,0), (0,-1), 'Helvetica-BoldOblique', 9),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f9f9f9')),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#666666')),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#d5dbdb')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        
        elements.append(tabela_dados_en)
        elements.append(Spacer(1, 25))

        # ===== RESUMO DA EMISSÃO - SEPARADO PT/EN =====
        
        emissao_local = EMISSOES_TRANSPORTE.get(registro['transporte_local'], 5.0) * registro['distancia_local'] * registro['dias_evento']
        emissao_principal = registro['emissao_total'] - emissao_local
        
        elements.append(Paragraph("RESUMO DA EMISSÃO", estilo_subtitulo))
        elements.append(Paragraph(f"TOTAL DE EMISSÕES: {registro['emissao_total']:.2f} kgCO2e", estilo_destaque))
        
        transporte_cidade_pt = registro['transporte_cidade'].capitalize()
        transporte_cidade_en = translations.get(registro['transporte_cidade']) or "City Transport"
        
        transporte_local_pt = registro['transporte_local'].capitalize()
        transporte_local_en = translations.get(registro['transporte_local']) or "Local Commute"
        
        # TABELA EM PORTUGUÊS
        detalhes_emissao_pt = [
            ["Tipo de Deslocamento", "Transporte", "Distância", "Emissão (kgCO2e)"],
            [
                "Até a cidade do evento", 
                transporte_cidade_pt, 
                f"{registro['distancia_cidade']} km", 
                f"{emissao_principal:.2f}"
            ],
            [
                "Deslocamento local", 
                transporte_local_pt, 
                f"{registro['distancia_local']} km/dia × {registro['dias_evento']} dias", 
                f"{emissao_local:.2f}"
            ],
            ["TOTAL", "", "", f"{registro['emissao_total']:.2f} kgCO2e"]
        ]
        
        tabela_emissao_pt = Table(detalhes_emissao_pt, colWidths=[5.5*cm, 3*cm, 4*cm, 3.5*cm])
        tabela_emissao_pt.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
            ('FONT', (0,-1), (-1,-1), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498db')),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('TEXTCOLOR', (0,-1), (-1,-1), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#7f8c8d')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        
        elements.append(tabela_emissao_pt)
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("EMISSIONS SUMMARY", estilo_subtitulo_en))
        elements.append(Paragraph(f"<font color='#666666'><i>TOTAL EMISSIONS: {registro['emissao_total']:.2f} kgCO2</i></font>", estilo_destaque_en))
        
        detalhes_emissao_en = [
            ["Trip Type", "Transport", "Distance", "Emissions (kgCO2e)"],
            [
                "To the event city", 
                transporte_cidade_en, 
                f"{registro['distancia_cidade']} km", 
                f"{emissao_principal:.2f}"
            ],
            [
                "Local commute", 
                transporte_local_en, 
                f"{registro['distancia_local']} km/day × {registro['dias_evento']} days", 
                f"{emissao_local:.2f}"
            ],
            ["TOTAL", "", "", f"{registro['emissao_total']:.2f} kgCO2e"]
        ]
        
        tabela_emissao_en = Table(detalhes_emissao_en, colWidths=[5.5*cm, 3*cm, 4*cm, 3.5*cm])
        tabela_emissao_en.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica-Oblique', 9),
            ('FONT', (0,0), (-1,0), 'Helvetica-BoldOblique', 10),
            ('FONT', (0,-1), (-1,-1), 'Helvetica-BoldOblique', 10),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#5dade2')),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#58d68d')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('TEXTCOLOR', (0,-1), (-1,-1), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#aab7b8')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        
        elements.append(tabela_emissao_en)
        elements.append(Spacer(1, 25))

        # ===== COMPARAÇÕES AMBIENTAIS - SEPARADO PT/EN =====
        
        arvores = registro['emissao_total'] / 7000000  # 1 árvore absorve ~7.000.000g CO2/ano ou 7 toneladas de CO2/ano
        lampadas = registro['emissao_total'] / 450   # 1 lâmpada LED/dia
        
        elements.append(Paragraph("IMPACTO AMBIENTAL - EQUIVALÊNCIAS", estilo_subtitulo))
        
        comparativos_pt = [
            ["Equivalência", "Valor Aproximado"],
            ["Árvores para absorver em 1 ano", f"{arvores:.2f} árvores"],
            ["Horas de lâmpada LED (60W)", f"{lampadas:.1f} horas"],
            ["Emissão diária média brasileira*", "≈ 12 kgCO2e"]
        ]
        
        tabela_comparativo_pt = Table(comparativos_pt, colWidths=[9*cm, 7*cm])
        tabela_comparativo_pt.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e67e22')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#d35400')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        
        elements.append(tabela_comparativo_pt)
        
        nota_pt = Paragraph(
            "* Baseado na média brasileira de 4.4 toneladas de CO2e per capita/ano",
            ParagraphStyle('Nota', parent=estilo_normal, fontSize=8, textColor=colors.gray)
        )
        elements.append(nota_pt)
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("ENVIRONMENTAL IMPACT - EQUIVALENCES", estilo_subtitulo_en))
        
        comparativos_en = [
            ["Equivalence", "Approximate Value"],
            ["Trees to absorb in 1 year", f"{arvores:.2f} trees"],
            ["Hours of LED bulb (60W)", f"{lampadas:.1f} hours"],
            ["Average daily Brazilian emission*", "≈ 12 kgCO2e"]
        ]
        
        tabela_comparativo_en = Table(comparativos_en, colWidths=[9*cm, 7*cm])
        tabela_comparativo_en.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica-Oblique', 9),
            ('FONT', (0,0), (-1,0), 'Helvetica-BoldOblique', 10),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f39c12')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#e67e22')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        
        elements.append(tabela_comparativo_en)
        
        nota_en = Paragraph(
            "<font color='#666666'><i>* Based on the Brazilian average of 4.4 tons of CO2e per capita/year</i></font>",
            ParagraphStyle('Nota', parent=estilo_normal, fontSize=8, textColor=colors.gray)
        )
        elements.append(nota_en)
        elements.append(Spacer(1, 25))

        # ===== RECOMENDAÇÕES - LISTAS SEPARADAS PT/EN =====
        
        elements.append(Paragraph("RECOMENDAÇÕES PARA REDUZIR EMISSÕES", estilo_subtitulo))
        
        recomendacoes_pt = [
            " Escolha acomodações próximas ao local do evento, reduzindo a necessidade de transporte motorizado",
            " Para distâncias curtas, opte por caminhar ou pedalar, formas ativas e sustentáveis de locomoção que também favorecem a saúde e o bem-estar",
            " Prefira transportes públicos ou coletivos para deslocamentos sempre que possível",
            " Organize caronas solidárias com outros participantes, otimizando o uso dos veículos e diminuindo o número de deslocamentos individuais",
            " Planeje seus deslocamentos com antecedência para evitar horários de tráfego intenso e, consequentemente, o aumento do consumo de combustível",
            " Dê preferência a veículos elétricos ou híbridos, quando disponíveis, para minimizar o impacto ambiental dos deslocamentos", 
            " Compense emissões participando de programas de reflorestamento ou outras iniciativas ambientais reconhecidas"
        ]
        
        for rec_pt in recomendacoes_pt:
            elements.append(Paragraph(f"• {rec_pt}", estilo_normal))
            elements.append(Spacer(1, 4))
        
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph("RECOMMENDATIONS TO REDUCE EMISSIONS", estilo_subtitulo_en))
        
        recomendacoes_en = [
            " Choose accommodations close to the event venue, reducing the need for motorized transport",
            " For short distances, choose walking or cycling, active and sustainable forms of mobility that also promote health and well-being",
            " Prefer public or collective transportation whenever possible",
            " Organize carpooling with other participants, optimizing vehicle use and reducing the number of individual trips",
            " Plan your trips in advance to avoid peak traffic times and consequently reduce fuel consumption",
            " Prefer electric or hybrid vehicles when available to minimize the environmental impact of travel", 
            " Compensate emissions by participating in reforestation programs or other recognized environmental initiatives"
        ]
        
        for rec_en in recomendacoes_en:
            elements.append(Paragraph(f"<font color='#666666'><i>• {rec_en}</i></font>", estilo_normal_en))
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 20))

        # ===== RODAPÉ SEPARADO PT/EN =====
        elements.append(Spacer(1, 10))
        linha_rodape = Table([[""]], colWidths=[16*cm], rowHeights=[1])
        linha_rodape.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#95a5a6')),
        ]))
        elements.append(linha_rodape)
        
        rodape_pt = Paragraph(
            "Calculadora de Emissão de CO2e - Eventos Esportivos Sustentáveis<br/>" +
            "Uma iniciativa da parceria entre CBVela e ETTA/UFF com o apoio do CNPq e Faperj para promover a conscientização ambiental em eventos esportivos",
            ParagraphStyle(
                'Rodape', 
                parent=estilo_normal, 
                fontSize=9, 
                alignment=1, 
                textColor=colors.HexColor('#7f8c8d'),
                spaceBefore=10
            )
        )
        elements.append(rodape_pt)
        
        elements.append(Spacer(1, 10))
        
        rodape_en = Paragraph(
            "<font color='#666666'><i>CO2e Emissions Calculator - Sustainable Sporting Events<br/>" +
            "An initiative of the partnership between CBVela and ETTA/UFF with support from CNPq and Faperj to promote environmental awareness in sporting events</i></font>",
            ParagraphStyle(
                'RodapeEn', 
                parent=estilo_normal, 
                fontSize=8, 
                alignment=1, 
                textColor=colors.HexColor('#95a5a6'),
                spaceBefore=5
            )
        )
        elements.append(rodape_en)

        # ===== GERAR PDF =====
        doc.build(elements)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Erro ao gerar PDF detalhado: {str(e)}")
        return gerar_pdf_simples(registro)
    
def gerar_pdf_simples(registro):
    """Fallback: PDF simples caso a versão detalhada falhe"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Cada Deslocamento Conta: Seu Impacto em CO2 no Evento")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"Email: {registro['email']}")
    p.drawString(100, 750, f"Tipo: {registro['tipo_participante']}")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 700, f"Emissão Total: {registro['emissao_total']:.2f} kgCO2")
    
    p.setFont("Helvetica", 10)
    p.drawString(100, 670, f"Transporte principal: {registro['transporte_cidade']}")
    p.drawString(100, 650, f"Distância: {registro['distancia_cidade']} km")
    p.drawString(100, 630, f"Transporte local: {registro['transporte_local']}")
    p.drawString(100, 610, f"Dias de evento: {registro['dias_evento']}")
    
    p.drawString(100, 550, "Uma iniciativa da parceria entre CBVela e ETTA/UFF com o apoio do CNPq e Faperj para promover aconscientização ambiental em eventos esportivos")
    p.drawString(100, 530, "Calculadora de Emissões - Eventos Sustentáveis")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def criar_tabela_simples(dados, col_widths, styles, header_color='#3498db'):
    """
    Cria uma tabela simples monolíngue com cabeçalho colorido.
    dados: lista de listas (primeira linha é cabeçalho)
    col_widths: larguras das colunas em cm
    styles: objeto StyleSheet do reportlab
    header_color: cor de fundo do cabeçalho (hex)
    """
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib import colors
    
    tabela_dados = []
    for i, linha in enumerate(dados):
        nova_linha = []
        for item in linha:
            if isinstance(item, str):
                if i == 0:  # cabeçalho
                    estilo = ParagraphStyle('Header', parent=styles['Normal'], 
                                            fontSize=10, textColor=colors.white, alignment=1)
                else:
                    estilo = styles['Normal']
                nova_linha.append(Paragraph(item, estilo))
            else:
                nova_linha.append(item)
        tabela_dados.append(nova_linha)
    
    tabela = Table(tabela_dados, colWidths=col_widths)
    tabela.setStyle(TableStyle([
        ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor(header_color)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    return tabela


# Rotas Flask
@app.route('/')
def index():
    return render_template('index.html',translations=translations)

@app.route('/questionario')
def questionario():
    return render_template('questionario.html', 
                          transportes=EMISSOES_TRANSPORTE.keys(),
                          tipos_participante=TIPOS_PARTICIPANTE,
                          #estados_brasil=ESTADOS_BRASIL,
                          paises_portugues=PAISES_PORTUGUES,  
                          paises_ingles=PAISES_INGLES,        
                          paises_dict=PAISES_DICT,            
                          translations=translations)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        dados_form = request.form
        
        pais_pt = dados_form.get('pais_origem', '').strip()
        if not pais_pt:
            return "Erro: Selecione um país de origem.", 400
        pais_en = PAISES_DICT.get(pais_pt, pais_pt)
        

        tipo_participante = dados_form['tipo_participante']
        if tipo_participante not in TIPOS_PARTICIPANTE:
            tipo_participante = "Outro"
        
        distancia_principal = float(dados_form['distancia_cidade'])
        transporte_principal = dados_form['transporte_cidade']
        emissao_principal = EMISSOES_TRANSPORTE.get(transporte_principal, 5.0) * distancia_principal

        custo_transporte = dados_form.get('custo_transporte', '')
        if custo_transporte:
            custo_transporte = float(custo_transporte)
        else:
            custo_transporte = None

        custo_diario = dados_form.get('custo_transporte_diario', '')
        if custo_diario and custo_diario.strip():
            try:
                custo_diario_valor = float(custo_diario)
            except ValueError:
                custo_diario_valor = None
        else:
            custo_diario_valor = None

        distancia_local = float(dados_form['distancia_local'])
        transporte_local = dados_form['transporte_local']
        dias_evento = int(dados_form['dias_evento'])
        emissao_local = EMISSOES_TRANSPORTE.get(transporte_local, 5.0) * distancia_local * dias_evento
        
        emissao_total = (emissao_principal + emissao_local)/1000  # Converte para kgCO2
        
        def processar_campo_numerico(nome_campo):
            valor = dados_form.get(nome_campo, '')
            if valor and valor.strip():
                try:
                    return float(valor)
                except ValueError:
                    return None
            return None
        
        custo_transporte = processar_campo_numerico('custo_transporte')
        custo_diario_valor = processar_campo_numerico('custo_transporte_diario')
        gasto_alimentacao_valor = processar_campo_numerico('gasto_alimentacao')      
        gasto_equipamentos_valor = processar_campo_numerico('gasto_equipamentos')    
        gasto_botes_valor = processar_campo_numerico('gasto_botes')                  
        gasto_hospedagem_valor = processar_campo_numerico('gasto_hospedagem')

        pontos_turisticos = dados_form.get('pontos_turisticos', '').strip()
        pontos_turisticos = pontos_turisticos if pontos_turisticos else None

        # Criar registro no banco
        with app.app_context():
            nova_resposta = RespostaEmissao(
                email=dados_form['email'],
#                estado_origem=dados_form['estado_origem'],
                pais_origem_pt=pais_pt,
                pais_origem_en=pais_en,
                tipo_participante=tipo_participante,
                transporte_cidade=transporte_principal,
                distancia_cidade=distancia_principal,
                custo_transporte=custo_transporte, 
                transporte_local=transporte_local,
                distancia_local=distancia_local,
                dias_evento=dias_evento,
                custo_transporte_diario=custo_diario_valor,

                gasto_alimentacao=gasto_alimentacao_valor,
                gasto_equipamentos=gasto_equipamentos_valor,
                gasto_botes=gasto_botes_valor,
                gasto_hospedagem=gasto_hospedagem_valor,
                pontos_turisticos=pontos_turisticos,
                

                emissao_total=emissao_total
            )
            
            db.session.add(nova_resposta)
            db.session.commit()
            
            resposta_id = nova_resposta.id
        
        # Gerar gráfico 
        grafico_base64 = gerar_grafico_base64()
        
        return render_template('resultados.html', 
                              registro=nova_resposta.to_dict(), 
                              grafico_base64=grafico_base64,
                              resposta_id=resposta_id,
                              paises_dict=PAISES_DICT,
                              translations=translations)
                              
    except Exception as e:
        print(f"Erro no submit: {e}")
        return f"Erro ao salvar dados: {str(e)}", 500

@app.route('/dados')
def get_dados():
    with app.app_context():
        respostas = RespostaEmissao.query.all()
        dados = {"respostas": [resposta.to_dict() for resposta in respostas]}
    return jsonify(dados)

@app.route('/download')
def download_dados():
    try:
        with app.app_context():
            respostas = RespostaEmissao.query.all()
        
        # Criar CSV
        si = StringIO()
        cw = csv.writer(si)
        cw.writerow(['ID', 'Email', 'País de Origem', 'Tipo Participante', 
                     'Transporte até a Cidade', 'Distância até a Cidade (km)', 'Custo Transporte (R$)', 
                     'Transporte Local', 'Distância Local (km)', 'Dias de Evento',
                     'Custo Transporte Diário (R$)','Gasto Alimentação (R$)', 
                     'Gasto Transporte Equipamentos (R$)', 'Gasto Aluguel Botes (R$)','Gasto Hospedagem (R$)',
                     'Pontos Turísticos Visitados','Emissão Total (kgCO2)'])
        
        for resposta in respostas:
            cw.writerow([
                resposta.id,
                resposta.email,
                f"{resposta.pais_origem_pt} / {resposta.pais_origem_en}",
             #   resposta.estado_origem,
                resposta.tipo_participante,
                resposta.transporte_cidade,
                float(resposta.distancia_cidade),
                float(resposta.custo_transporte) if resposta.custo_transporte else '',  
                resposta.transporte_local,
                float(resposta.distancia_local),
                resposta.dias_evento,
                float(resposta.custo_transporte_diario) if resposta.custo_transporte_diario else '',
                float(resposta.gasto_alimentacao) if resposta.gasto_alimentacao else '',
                float(resposta.gasto_equipamentos) if resposta.gasto_equipamentos else '',
                float(resposta.gasto_botes) if resposta.gasto_botes else '',
                float(resposta.gasto_hospedagem) if resposta.gasto_hospedagem else '',
                resposta.pontos_turisticos if resposta.pontos_turisticos else '',
                
                float(resposta.emissao_total),
            ])
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=emissoes_co2_regata.csv"
        output.headers["Content-type"] = "text/csv"
        return output
        
    except Exception as e:
        return f"Erro ao gerar CSV: {str(e)}", 500

@app.route('/download-pdf/<int:resposta_id>')
def download_pdf(resposta_id):
    try:
        with app.app_context():
            resposta = RespostaEmissao.query.get_or_404(resposta_id)
        
        pdf_buffer = gerar_pdf(resposta.to_dict())
        email_parte = resposta.email.split('@')[0] if resposta.email else 'sem_email'
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"emissao_co2_{email_parte}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"Erro ao gerar PDF: {str(e)}", 500

# Inicialização 
def init_database():
    with app.app_context():
        try:
            db.create_all()
            print("✅ Banco de dados inicializado com sucesso!")
            print(f"✅ Usando banco: {app.config['SQLALCHEMY_DATABASE_URI']}")
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")

if __name__ == '__main__':
    init_database()
    print("🚀 Servidor iniciando em http://127.0.0.1:5000")
    app.run(debug=True)



