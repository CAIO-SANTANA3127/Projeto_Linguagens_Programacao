# 📊 Análise do Desemprego no Brasil (2015–2024)

> Projeto de análise e visualização de dados · Disciplina: Análise e Visualização de Dados · G2

---

## 🎯 Sobre o Projeto

Este projeto apresenta uma análise executiva do mercado de trabalho brasileiro,
considerando taxa de desemprego, renda média, vagas formais, inflação, nível de risco
e distribuição por estado, região e setor econômico.

A proposta demonstra um fluxo completo de projeto analítico:
preparação dos dados → análise exploratória → criação de KPIs →
visualizações → dashboard interativo → publicação em ambiente web.

---

## ❓ Perguntas de Negócio

- Qual é a taxa média de desemprego no Brasil no período?
- Quais regiões concentram o maior desemprego?
- Como a pandemia afetou os indicadores de trabalho?
- Qual setor econômico registra maior precariedade?
- Existe correlação entre inflação e desemprego?
- Quais estados geram mais vagas formais?

---

## 📐 Indicadores Analisados

| KPI | Descrição |
|---|---|
| **Taxa de Desemprego** | Percentual da população ativa sem emprego |
| **Renda Média** | Salário médio dos trabalhadores por UF/setor |
| **Vagas Formais** | Total de empregos com carteira assinada |
| **Nível de Risco** | Classificação qualitativa (Baixo / Médio / Alto / Crítico) |
| **Inflação** | Taxa de inflação acumulada por período |

---

## 🛠️ Tecnologias Utilizadas

**Obrigatórias**

| Tecnologia | Uso |
|---|---|
| Python 3.11 | Linguagem principal |
| Pandas | Manipulação e análise de dados |
| Matplotlib / Seaborn | Visualizações estáticas no notebook |
| Streamlit | Dashboard interativo |
| GitHub / GitHub Pages | Publicação do código e da página web |

**Intermediárias** (todas implementadas)
- Filtros múltiplos no Streamlit
- KPIs dinâmicos
- Análise temporal
- Dashboards organizados em seções (abas)
- Visualizações comparativas

**Avançadas** (implementadas)
- Persistência em banco — SQLAlchemy + SQLite
- Mapas interativos — Plotly scatter_geo
- Correlação estatística — Pandas / NumPy

---

## 📁 Estrutura do Projeto

```
projeto-desemprego-brasil/
│
├── app.py                   ← Dashboard Streamlit (multipágina)
├── requirements.txt
├── README.md
├── index.html               ← Página GitHub Pages
│
├── dados/
│   └── simulacao_desemprego_brasil.csv
│
├── database/
│   └── db.py                ← SQLAlchemy + SQLite
│
├── notebooks/
│   └── analise_desemprego_brasil.ipynb
│
└── imagens/
    └── (gráficos gerados pelo notebook)
```

---

## 🚀 Como Executar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/projeto-desemprego-brasil.git
cd projeto-desemprego-brasil

# 2. Crie um ambiente virtual e instale as dependências
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 3. Execute o dashboard
streamlit run app.py

# Se o PowerShell disser que "streamlit" não é reconhecido, use:
python -m streamlit run app.py

# Evite rodar com "python app.py" (isso executa em modo bare e não abre o app no navegador)
```

---

## 🔗 Links de Acesso

| Recurso | Link |
|---|---|
| Repositório GitHub | `https://github.com/seu-usuario/projeto-desemprego-brasil` |
| GitHub Pages | `https://seu-usuario.github.io/projeto-desemprego-brasil` |
| Dashboard Streamlit | `https://7pk6bstknerbywz4ojgh9y.streamlit.app/` |

---

## 📊 Principais Conclusões

1. **Nordeste** registra as maiores taxas de desemprego (CE 13,65%, PB 13,47%, BA 13,35%)
2. **Sul** lidera os menores índices nacionais (PR 6,71%, SC 6,75%, RS 6,92%)
3. **2020–2021** representou o pico de desemprego, associado à pandemia de COVID-19
4. **Construção Civil** apresenta o maior percentual de desemprego setorial
5. Correlação fraca entre inflação e desemprego — outros vetores são mais determinantes

---

*Desenvolvido como projeto de avaliação G2 · Caio de Santana Pereira*
