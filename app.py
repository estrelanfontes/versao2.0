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

# Configuração ROBUSTA com fallback
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#Etapa Render
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # PRODUÇÃO (Render) - Converte postgres:// para postgresql:// se necessário
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
# SEU MODELO ORIGINAL (mantenha igual)
class RespostaEmissao(db.Model):
    __tablename__ = 'respostas_emissao'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    estado_origem = db.Column(db.String(100), nullable=False)
    tipo_participante = db.Column(db.String(50), nullable=False)
    transporte_cidade = db.Column(db.String(50), nullable=False)
    distancia_cidade = db.Column(db.Numeric(10, 2), nullable=False)
    transporte_local = db.Column(db.String(50), nullable=False)
    distancia_local = db.Column(db.Numeric(10, 2), nullable=False)
    dias_evento = db.Column(db.Integer, nullable=False)
    emissao_total = db.Column(db.Numeric(10, 2), nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'estado_origem': self.estado_origem,
            'tipo_participante': self.tipo_participante,
            'transporte_cidade': self.transporte_cidade,
            'distancia_cidade': float(self.distancia_cidade),
            'transporte_local': self.transporte_local,
            'distancia_local': float(self.distancia_local),
            'dias_evento': self.dias_evento,
            'emissao_total': float(self.emissao_total),
            'data': self.data_registro.strftime("%Y-%m-%d %H:%M:%S")
        }

# Dados de emissão por transporte (gCO2/km)
EMISSOES_TRANSPORTE = {
    "carro": 96.6,
    "ônibus": 67,
    "avião": 43,
    "barca": 59,
    "bicicleta/a pé": 0,
    "moto": 80.5,
    "trem": 21,
    "outros": 50
}

# Lista de tipos de participantes
TIPOS_PARTICIPANTE = [
    "Velejador/Velejadora",
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

# Função para gerar gráfico
def gerar_grafico_base64():
    try:
        with app.app_context():
            respostas = RespostaEmissao.query.all()
        
        if not respostas:
            return None
        
        emissoes_transporte = {transp: 0 for transp in EMISSOES_TRANSPORTE.keys()}
        emissoes_tipo = {tipo: 0 for tipo in TIPOS_PARTICIPANTE}
        
        for resposta in respostas:
            transp = resposta.transporte_cidade
            if transp in emissoes_transporte:
                emissoes_transporte[transp] += float(resposta.emissao_total)
            
            tipo = resposta.tipo_participante
            if tipo in emissoes_tipo:
                emissoes_tipo[tipo] += float(resposta.emissao_total)
        
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))
        fig.suptitle('Análise de Emissões de CO2 - Regata', fontsize=16, fontweight='bold')
        
        # Gráfico 1: Emissões por tipo de transporte
        transportes_validos = [t for t in emissoes_transporte.keys() if emissoes_transporte[t] > 0]
        valores_transp = [emissoes_transporte[t] for t in transportes_validos]
        
        if transportes_validos and any(valores_transp):
    # Cores manualmente distribuídas
            num_cores = len(transportes_validos)
            cores1 = [plt.cm.Set3(i / max(num_cores, 1)) for i in range(num_cores)]
            ax1.pie(valores_transp, labels=transportes_validos, autopct='%1.1f%%', colors=cores1)
            ax1.set_title("Distribuição de Emissões por Tipo de Transporte")
        
        # Gráfico 2: Emissões por tipo de participante
        tipos_validos = [t for t in TIPOS_PARTICIPANTE if emissoes_tipo[t] > 0]
        valores_tipos = [emissoes_tipo[t] for t in tipos_validos]
        
        if tipos_validos:
            num_cores = len(tipos_validos)
            cores2 = [plt.cm.viridis(i / max(num_cores, 1)) for i in range(num_cores)]
            bars = ax2.bar(tipos_validos, valores_tipos, color=cores2)
            ax2.set_title("Emissões por Tipo de Participante")
            ax2.set_ylabel("Emissão de CO2 (g)")
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            for bar, valor in zip(bars, valores_tipos):
                height = bar.get_height()
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                            f'{valor:.2f}g', ha='center', va='bottom', fontsize=8)
        
        # Gráfico 3: Eficiência dos transportes
        eficiencias = list(EMISSOES_TRANSPORTE.values())
        transportes_efic = list(EMISSOES_TRANSPORTE.keys())
        
        bars = ax3.bar(transportes_efic, eficiencias, color='#FF9800')
        ax3.set_title("Eficiência de Emissão por Tipo de Transporte")
        ax3.set_ylabel("gCO2 por km")
        ax3.set_xlabel("Tipo de Transporte")
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        
        for bar, valor in zip(bars, eficiencias):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{valor:.2f}g', ha='center', va='bottom')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64
        
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
        return None

# Funções de PDF
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
    """Gera PDF com os resultados do questionário"""
    try:
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=72, 
            leftMargin=72,
            topMargin=72, 
            bottomMargin=18,
            title=f"Emissão CO2 - {registro['email']}"
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        estilo_titulo = ParagraphStyle(
            'TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1
        )
        
        estilo_subtitulo = ParagraphStyle(
            'Subtitulo',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#34495e'),
            borderPadding=5
        )
        
        estilo_normal = ParagraphStyle(
            'NormalCustom',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        estilo_destaque = ParagraphStyle(
            'Destaque',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#27ae60'),
            alignment=1
        )

        # ===== CABEÇALHO =====
        titulo = Paragraph("Cada Deslocamento Conta: Seu Impacto em CO2 no Evento", estilo_titulo)
        elements.append(titulo)
        
        linha_divisoria = Table([[""]], colWidths=[16*cm], rowHeights=[1])
        linha_divisoria.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#3498db')),
            ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#3498db')),
        ]))
        elements.append(linha_divisoria)
        elements.append(Spacer(1, 20))

        # ===== DADOS DO PARTICIPANTE =====
        elements.append(Paragraph("DADOS DO PARTICIPANTE", estilo_subtitulo))
        
        dados_pessoais = [
            ["Local de Origem:", 
             "Estrangeiro" if registro.get('estado_origem') == "Não se aplica (estrangeiro)" 
             else registro.get('estado_origem', 'Não informado')],
            ["Tipo de Participante:", registro['tipo_participante']],
            ["Email:", registro['email']],
            ["Data do Cálculo:", registro['data']]
        ]
        
        tabela_dados = Table(dados_pessoais, colWidths=[4*cm, 10*cm])
        tabela_dados.setStyle(TableStyle([
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
        
        elements.append(tabela_dados)
        elements.append(Spacer(1, 25))

        # ===== RESUMO DA EMISSÃO =====
        elements.append(Paragraph("RESUMO DA EMISSÃO", estilo_subtitulo))
        
        # Cálculo detalhado
        emissao_local = EMISSOES_TRANSPORTE.get(registro['transporte_local'], 5.0) * registro['distancia_local'] * registro['dias_evento']
        emissao_principal = registro['emissao_total'] - emissao_local
        
        emissao_total = Paragraph(
            f"<b>TOTAL DE EMISSÕES: {registro['emissao_total']:.2f} gCO2</b>", 
            estilo_destaque
        )
        elements.append(emissao_total)
        elements.append(Spacer(1, 15))

        detalhes_emissao = [
            ["Tipo de Deslocamento", "Transporte", "Distância", "Emissão (gCO2)"],
            [
                "Até a cidade do evento", 
                registro['transporte_cidade'].capitalize(), 
                f"{registro['distancia_cidade']} km", 
                f"{emissao_principal:.2f}"
            ],
            [
                "Deslocamento local", 
                registro['transporte_local'].capitalize(), 
                f"{registro['distancia_local']} km/dia × {registro['dias_evento']} dias", 
                f"{emissao_local:.2f}"
            ],
            ["TOTAL", "", "", f"<b>{registro['emissao_total']:.2f} gCO2</b>"]
        ]
        
        tabela_emissao = Table(detalhes_emissao, colWidths=[5.5*cm, 3*cm, 4*cm, 3.5*cm])
        tabela_emissao.setStyle(TableStyle([
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
        
        elements.append(tabela_emissao)
        elements.append(Spacer(1, 25))

        # ===== COMPARAÇÕES AMBIENTAIS =====
        elements.append(Paragraph("IMPACTO AMBIENTAL - EQUIVALÊNCIAS", estilo_subtitulo))
        
        arvores = registro['emissao_total'] / 21000  # 1 árvore absorve ~21kg CO2/ano
        lampadas = registro['emissao_total'] / 450   # 1 lâmpada LED/dia
        
        comparativos = [
            ["Equivalência", "Valor Aproximado"],
            ["Árvores para absorver em 1 ano", f"{arvores:.2f} árvores"],
            ["Horas de lâmpada LED (60W)", f"{lampadas:.1f} horas"],
            ["Emissão diária média brasileira*", "≈ 12.000 gCO2"]
        ]
        
        tabela_comparativo = Table(comparativos, colWidths=[9*cm, 7*cm])
        tabela_comparativo.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'Helvetica', 9),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e67e22')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#d35400')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        
        elements.append(tabela_comparativo)
        elements.append(Spacer(1, 10))
        
        nota = Paragraph(
            "* Baseado na média brasileira de 4.4 toneladas de CO2 per capita/ano",
            ParagraphStyle('Nota', parent=estilo_normal, fontSize=8, textColor=colors.gray)
        )
        elements.append(nota)
        elements.append(Spacer(1, 25))

        # ===== RECOMENDAÇÕES =====
        elements.append(Paragraph("RECOMENDAÇÕES PARA REDUZIR EMISSÕES", estilo_subtitulo))
        
        recomendacoes = [
            "🏨 Escolha acomodações próximas ao local do evento, reduzindo a necessidade de transporte motorizado",
            "🚶 Para distâncias curtas, opte por caminhar ou pedalar, formas ativas e sustentáveis de locomoção que também favorecem a saúde e o bem-estar",
            "🌱 Prefira transportes públicos ou coletivos para deslocamentos sempre que possível",
            "🚗 Organize caronas solidárias com outros participantes, otimizando o uso dos veículos e diminuindo o número de deslocamentos individuais",
            "📅 Planeje seus deslocamentos com antecedência para evitar horários de tráfego intenso e, consequentemente, o aumento do consumo de combustível",
            "💡 Dê preferência a veículos elétricos ou híbridos, quando disponíveis, para minimizar o impacto ambiental dos deslocamentos", 
            "🌳 Compense emissões participando de programas de reflorestamento ou outras iniciativas ambientais reconhecidas"
        ]
        
        for rec in recomendacoes:
            elements.append(Paragraph(rec, estilo_normal))
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 20))

        # ===== RODAPÉ =====
        elements.append(Spacer(1, 10))
        linha_rodape = Table([[""]], colWidths=[16*cm], rowHeights=[1])
        linha_rodape.setStyle(TableStyle([
            ('LINEABOVE', (0,0), (-1,-1), 1, colors.HexColor('#95a5a6')),
        ]))
        elements.append(linha_rodape)
        
        rodape = Paragraph(
            "Calculadora de Emissão de CO2 - Eventos Esportivos Sustentáveis<br/>" +
            "Relatório gerado automaticamente - Juntos por um planeta mais verde!",
            ParagraphStyle(
                'Rodape', 
                parent=estilo_normal, 
                fontSize=9, 
                alignment=1, 
                textColor=colors.HexColor('#7f8c8d'),
                spaceBefore=10
            )
        )
        elements.append(rodape)

        # ===== GERAR PDF =====
        doc.build(elements)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
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
    p.drawString(100, 700, f"Emissão Total: {registro['emissao_total']:.2f} gCO2")
    
    p.setFont("Helvetica", 10)
    p.drawString(100, 670, f"Transporte principal: {registro['transporte_cidade']}")
    p.drawString(100, 650, f"Distância: {registro['distancia_cidade']} km")
    p.drawString(100, 630, f"Transporte local: {registro['transporte_local']}")
    p.drawString(100, 610, f"Dias de evento: {registro['dias_evento']}")
    
    p.drawString(100, 550, "Relatório gerado automaticamente")
    p.drawString(100, 530, "Calculadora de Emissões - Eventos Sustentáveis")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# Rotas Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questionario')
def questionario():
    return render_template('questionario.html', 
                          transportes=EMISSOES_TRANSPORTE.keys(),
                          tipos_participante=TIPOS_PARTICIPANTE,
                          estados_brasil=ESTADOS_BRASIL)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        dados_form = request.form
        
        # Validações e cálculos
        tipo_participante = dados_form['tipo_participante']
        if tipo_participante not in TIPOS_PARTICIPANTE:
            tipo_participante = "Outro"
        
        distancia_principal = float(dados_form['distancia_cidade'])
        transporte_principal = dados_form['transporte_cidade']
        emissao_principal = EMISSOES_TRANSPORTE.get(transporte_principal, 5.0) * distancia_principal
        
        distancia_local = float(dados_form['distancia_local'])
        transporte_local = dados_form['transporte_local']
        dias_evento = int(dados_form['dias_evento'])
        emissao_local = EMISSOES_TRANSPORTE.get(transporte_local, 5.0) * distancia_local * dias_evento
        
        emissao_total = emissao_principal + emissao_local
        
        # Criar registro no banco
        with app.app_context():
            nova_resposta = RespostaEmissao(
                email=dados_form['email'],
                estado_origem=dados_form['estado_origem'],
                tipo_participante=tipo_participante,
                transporte_cidade=transporte_principal,
                distancia_cidade=distancia_principal,
                transporte_local=transporte_local,
                distancia_local=distancia_local,
                dias_evento=dias_evento,
                emissao_total=emissao_total
            )
            
            db.session.add(nova_resposta)
            db.session.commit()
            
            resposta_id = nova_resposta.id
        
        # Gerar gráfico atualizado
        grafico_base64 = gerar_grafico_base64()
        
        return render_template('resultados.html', 
                              registro=nova_resposta.to_dict(), 
                              grafico_base64=grafico_base64,
                              resposta_id=resposta_id)
                              
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
        cw.writerow(['ID', 'Email', 'Estado Origem', 'Tipo Participante', 
                     'Transporte até a Cidade', 'Distância até a Cidade (km)', 
                     'Transporte Local', 'Distância Local (km)', 'Dias de Evento', 
                     'Emissão Total (gCO2)', 'Data Registro'])
        
        for resposta in respostas:
            cw.writerow([
                resposta.id,
                resposta.email,
                resposta.estado_origem,
                resposta.tipo_participante,
                resposta.transporte_cidade,
                float(resposta.distancia_cidade),
                resposta.transporte_local,
                float(resposta.distancia_local),
                resposta.dias_evento,
                float(resposta.emissao_total),
                resposta.data_registro.strftime("%Y-%m-%d %H:%M:%S")
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
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"emissao_co2_{resposta.email.split('@')[0]}_{resposta.data_registro.strftime('%Y-%m-%d')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return f"Erro ao gerar PDF: {str(e)}", 500

# Inicialização SEGURA
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


