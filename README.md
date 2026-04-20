# Questionário Sustentável para Eventos Náuticos Esportivos

## Apresentação do projeto com parceria CNPq, Faperj, UFF e CBVela;
Este projeto tem como objetivo principal medir os impactos ambientais das emissões de carbono durante eventos náuticos;
Este trabalho também gera análises aproximadas sobre impacto ecônomico dos participantes na região sede;
A proposta é apresentar um questionário simples e intuitivo para que os integrantes preencham com facilidade.

Buscamos coletar principalmente a quilômetragem percorrida por cada indivíduo em seu deslocamento durante o evento,
seu gasto monetário médio para cada categoria especificada (aluguel de equipamentos, alimentação hospedagem e afins).
Também coletamos o Estado/País de origem dos participantes, o que permite análises distribuidas geograficamente sobre regiões que 
mais influenciaram os impactos ambientais e econômicos do evento em questão.

Ao final do questionário é apresentado uma interface gráfica com uma análise prévia e individual sobre os impactos. 
O usuário tem acesso a quantidade aproximada de carbono emitida por ele e alguns gráficos relevantes: Distribuição Econômica por Categoria, Distribuição de Emissão de CO2 por Tipo de Participante, Transporte mais Utilizado para Chegar ao Local do Evento e Transporte mais Utilizado no
dia a dia do Evento. Há uma ênfase nos meios de transporte neste diagnóstico pois são os principais fatores emissão de carbono neste contexto.
Além disso o usuário recebe um breve relatório com seus dados pessoais coletados, resultados de emissão individual e sugestões para reduzir os
impactos ambientais de forma simples e sustentável.

Com isso esperamos conscientizar toda a comunidade que compôs o evento e induzir uma redução nos impactos dos seguintes, tornando o esporte cada 
vez mais sustentável.

## Funcionalidades
- ✅ Coleta de quilometragem percorrida e gastos por categoria
- ✅ Cálculo individual de emissão de CO₂
- ✅ Gráficos de distribuição econômica e ambiental
- ✅ Relatório com sugestões sustentáveis personalizadas

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Descrição da Estrutura
O programa do questionário utiliza basicamente três linguagens: python, CSS, HTML;
Utiliza "Flask" como framework para aplicações web WSGI;
O arquivo app.py é utilizado como a matriz do projeto;
A pasta static contém a estrutura do design do projeto;
A pasta templates contém os arquivos index, questionario e resultados que contém respectivamente:
o desenvolvimento da tela inicial com uma breve apresentação do projeto,
o conjunto de perguntas que integram o questionário,
a interface gráfica com os resultados individuais.

versao2.0/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências
├── runtime.txt            # Versão Python (deploy)
├── render.yaml            # Configuração Render
├── script.js              # Gráficos e interatividade
├── static/                # CSS, imagens
├── templates/             # HTML (index, questionario, resultados)
└── README.md


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
## Instalação e execução
``bash
git clone https://github.com/estrelanfontes/versao2.0.git
cd versao2.0
pip install -r requirements.txt
python app.py
Server: http://127.0.0.1:5000

## License
