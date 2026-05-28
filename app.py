"""
app.py — Dashboard Interativo: Desemprego no Brasil (2015–2024)
Disciplina: Análise e Visualização de Dados
Aluno: Caio de Santana Pereira

Funcionalidades implementadas:
  Intermediárias → filtros múltiplos, KPIs dinâmicos, análise temporal,
                   dashboards em seções, visualizações comparativas
  Avançadas      → persistência SQLAlchemy + SQLite, mapas interativos (Plotly),
                   correlação estatística (Pandas/NumPy)
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from database.db import carregar_dataframe


# ── Execução correta (Streamlit runner) ───────────────────────────────────────
# Se você rodar este arquivo com `python app.py`, o Streamlit entra em "bare mode"
# e não inicializa o runtime/ScriptRunContext (gera warnings e não abre no browser).
# Para evitar confusão, exibimos uma dica e encerramos cedo.
_runtime_exists = True
try:
    _runtime_exists = bool(st.runtime.exists())  # Streamlit >= 1.20
except Exception:
    _runtime_exists = True

if not _runtime_exists:
    print(
        "Este arquivo é um app Streamlit. Execute assim:\n\n"
        "  python -m streamlit run app.py\n",
        file=sys.stderr,
    )
    raise SystemExit(0)

# ── Configuração da página ─────────────────────────────────────────────────────
from PIL import Image

_logo = Image.open("imagens/logo1.png")

st.set_page_config(
    page_title="Desemprego no Brasil · G2",
    page_icon=_logo,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ──────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif !important;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #1e293b;
  }
  [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stMultiSelect label,
  [data-testid="stSidebar"] .stSlider label { color: #94a3b8 !important; font-size: .8rem !important; font-weight: 500; letter-spacing: .03em; text-transform: uppercase; }
  [data-testid="stSidebar"] h1 { color: #f1f5f9 !important; font-size: 1rem !important; font-weight: 700; letter-spacing: -.01em; }
  [data-testid="stSidebar"] .stCaption { color: #475569 !important; }
  [data-testid="stSidebar"] [data-testid="stDivider"] { border-color: #1e293b !important; }

  /* Metrics */
  [data-testid="stMetric"] {
    background: #f8fafc;
    border-radius: 8px;
    padding: 18px 20px;
    border: 1px solid #e2e8f0;
  }
  [data-testid="stMetricLabel"] { font-size: .72rem !important; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: #64748b !important; }
  [data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 800 !important; color: #0f172a !important; letter-spacing: -.03em; }

  /* Section title */
  .section-title {
    font-size: .95rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -.01em;
    padding-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
    margin: 4px 0 16px;
  }

  /* Insight & warning boxes */
  .insight-box {
    background: #f0f9ff;
    border-left: 3px solid #2563eb;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    font-size: .875rem;
    color: #1e3a8a;
    line-height: 1.6;
  }
  .warning-box {
    background: #fffbeb;
    border-left: 3px solid #d97706;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    font-size: .875rem;
    color: #92400e;
    line-height: 1.6;
  }

  /* Tabs */
  [data-testid="stTabs"] [role="tab"] {
    font-weight: 600 !important;
    font-size: .85rem !important;
    letter-spacing: -.01em;
    color: #64748b !important;
  }
  [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #0f172a !important;
  }

  /* General cleanup */
  h1 { font-weight: 800 !important; letter-spacing: -.03em !important; color: #0f172a !important; }
  h2, h3 { font-weight: 700 !important; letter-spacing: -.02em !important; color: #0f172a !important; }
  [data-testid="stMarkdownContainer"] p { color: #475569; font-size: .9rem; }
  .stDivider { border-color: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Carga de dados ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Carregando dados do banco SQLite…")
def load_data() -> pd.DataFrame:
    return carregar_dataframe()

df_raw = load_data()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTROS MÚLTIPLOS  (funcionalidade intermediária)
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image(_logo, width=160)
    st.title("Filtros")

    anos = sorted(df_raw["ano"].unique())
    ano_min, ano_max = st.select_slider(
        "Período (ano)",
        options=anos,
        value=(anos[0], anos[-1]),
    )

    regioes_disponiveis = sorted(df_raw["regiao"].unique())
    regioes_sel = st.multiselect(
        "Região",
        options=regioes_disponiveis,
        default=regioes_disponiveis,
    )

    ufs_disponiveis = sorted(
        df_raw[df_raw["regiao"].isin(regioes_sel)]["uf"].unique()
    )
    ufs_sel = st.multiselect(
        "Estado (UF)",
        options=ufs_disponiveis,
        default=ufs_disponiveis,
    )

    setores_disponiveis = sorted(df_raw["setor_predominante"].unique())
    setores_sel = st.multiselect(
        "Setor predominante",
        options=setores_disponiveis,
        default=setores_disponiveis,
    )

    riscos_disponiveis = ["Baixo", "Médio", "Alto", "Crítico"]
    riscos_sel = st.multiselect(
        "Nível de risco",
        options=riscos_disponiveis,
        default=riscos_disponiveis,
    )

    st.divider()
    st.caption("Fonte: Simulação IBGE/Brasil · 2015–2024")

# ── Aplicar filtros ────────────────────────────────────────────────────────────
df = df_raw[
    (df_raw["ano"] >= ano_min) &
    (df_raw["ano"] <= ano_max) &
    (df_raw["regiao"].isin(regioes_sel)) &
    (df_raw["uf"].isin(ufs_sel)) &
    (df_raw["setor_predominante"].isin(setores_sel)) &
    (df_raw["nivel_risco"].isin(riscos_sel))
].copy()

# ── Cabeçalho principal ────────────────────────────────────────────────────────
st.title("Análise do Desemprego no Brasil (2015–2024)")
st.markdown(
    "Dashboard interativo com indicadores de mercado de trabalho, "
    "distribuição regional, setorial e análise de correlações estatísticas."
)

if df.empty:
    st.error("Nenhum registro encontrado para os filtros selecionados.")
    st.stop()

st.markdown(f"**{len(df):,} registros** carregados com os filtros aplicados.")
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# NAVEGAÇÃO — ABAS (dashboard multipágina)
# ══════════════════════════════════════════════════════════════════════════════
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "Visão Geral",
    "Série Temporal",
    "Análise Regional",
    "Setores",
    "Correlações",
])


# ══════════════════════════════════════════════════════════════════════════════
# ABA 1 — VISÃO GERAL / KPIs DINÂMICOS
# ══════════════════════════════════════════════════════════════════════════════
with aba1:
    st.markdown('<div class="section-title">Indicadores-chave</div>',
                unsafe_allow_html=True)

    taxa_media   = df["taxa_desemprego"].mean()
    renda_media  = df["renda_media"].mean()
    total_desemp = df["desempregados"].sum()
    total_vagas  = df["vagas_formais"].sum()
    infl_media   = df["inflacao"].mean()
    pop_ativa    = df["populacao_ativa"].sum()

    def brl_decimal(x, decimals=1):
        return f"{x:.{decimals}f}".replace(".", ",")

    def brl_milhar(x):
        return f"{int(x):,}".replace(",", ".")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Taxa Média de Desemprego", f"{brl_decimal(taxa_media)}%")
    c2.metric("Renda Média (R$)",         "R$ " + f"{renda_media:,.0f}".replace(",", "."))
    c3.metric("Total Desempregados",      brl_milhar(total_desemp))
    c4.metric("Vagas Formais",            brl_milhar(total_vagas))
    c5.metric("Inflação Média",           f"{brl_decimal(infl_media)}%")

    st.divider()

    # Distribuição risco
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">Distribuição por Nível de Risco</div>',
                    unsafe_allow_html=True)
        risk_counts = df["nivel_risco"].value_counts().reset_index()
        risk_counts.columns = ["nivel_risco", "quantidade"]
        cores_risco = {
            "Baixo": "#22c55e", "Médio": "#facc15",
            "Alto": "#f97316", "Crítico": "#ef4444",
        }
        fig_pizza = px.pie(
            risk_counts, names="nivel_risco", values="quantidade",
            color="nivel_risco", color_discrete_map=cores_risco,
            hole=0.45,
        )
        fig_pizza.update_traces(textposition="outside", textinfo="percent+label")
        fig_pizza.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig_pizza, width="stretch")

    with col_b:
        st.markdown('<div class="section-title">Taxa de Desemprego por Setor</div>',
                    unsafe_allow_html=True)
        setor_df = (df.groupby("setor_predominante")["taxa_desemprego"]
                    .mean().reset_index()
                    .sort_values("taxa_desemprego"))
        fig_setor = px.bar(
            setor_df, x="taxa_desemprego", y="setor_predominante",
            orientation="h", text_auto=".1f",
            color="taxa_desemprego", color_continuous_scale="Blues",
            labels={"taxa_desemprego": "Taxa Média (%)", "setor_predominante": ""},
        )
        fig_setor.update_layout(margin=dict(t=20, b=20), coloraxis_showscale=False)
        st.plotly_chart(fig_setor, width="stretch")

    # Tabela resumo por UF
    st.markdown('<div class="section-title">Resumo por Estado</div>',
                unsafe_allow_html=True)
    tabela_uf = (df.groupby(["uf", "regiao"])
                 .agg(
                     taxa_media=("taxa_desemprego", "mean"),
                     renda_media=("renda_media", "mean"),
                     desempregados=("desempregados", "sum"),
                     vagas=("vagas_formais", "sum"),
                 )
                 .reset_index()
                 .sort_values("taxa_media", ascending=False)
                 .rename(columns={
                     "uf": "UF", "regiao": "Região",
                     "taxa_media": "Taxa Média (%)", "renda_media": "Renda Média (R$)",
                     "desempregados": "Desempregados", "vagas": "Vagas Formais",
                 }))
    def fmt_brl(x):
        return "R$ " + f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def fmt_int(x):
        return f"{int(x):,}".replace(",", ".")

    tabela_uf["Taxa Média (%)"]   = tabela_uf["Taxa Média (%)"].apply(lambda x: f"{x:.2f}".replace(".", ","))
    tabela_uf["Renda Média (R$)"] = tabela_uf["Renda Média (R$)"].apply(fmt_brl)
    tabela_uf["Desempregados"]    = tabela_uf["Desempregados"].apply(fmt_int)
    tabela_uf["Vagas Formais"]    = tabela_uf["Vagas Formais"].apply(fmt_int)
    st.dataframe(tabela_uf, width="stretch", hide_index=True)

    st.markdown(
        '<div class="insight-box"><b>Insight:</b> O Nordeste concentra '
        'as maiores taxas de desemprego do país, liderado por CE, PB e BA. '
        'A região Sul apresenta consistentemente os melhores indicadores de '
        'empregabilidade, com taxas abaixo de 7%.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ABA 2 — SÉRIE TEMPORAL
# ══════════════════════════════════════════════════════════════════════════════
with aba2:
    st.markdown('<div class="section-title">Evolução da Taxa de Desemprego</div>',
                unsafe_allow_html=True)

    serie_ano = (df.groupby("ano")
                 .agg(
                     taxa_media=("taxa_desemprego", "mean"),
                     renda_media=("renda_media", "mean"),
                     desempregados=("desempregados", "sum"),
                     inflacao=("inflacao", "mean"),
                 )
                 .reset_index())

    fig_linha = px.line(
        serie_ano, x="ano", y="taxa_media",
        markers=True, text=serie_ano["taxa_media"].round(1),
        labels={"ano": "Ano", "taxa_media": "Taxa de Desemprego (%)"},
        color_discrete_sequence=["#2563eb"],
    )
    fig_linha.update_traces(
        textposition="top center",
        line=dict(width=3),
        marker=dict(size=8),
    )
    fig_linha.add_vrect(x0=2019.5, x1=2021.5,
                        fillcolor="#fef08a", opacity=0.35,
                        annotation_text="Pandemia COVID-19",
                        annotation_position="top left")
    fig_linha.update_layout(margin=dict(t=40, b=20))
    st.plotly_chart(fig_linha, width="stretch")

    # Taxa por região ao longo do tempo
    st.markdown('<div class="section-title">Evolução por Região</div>',
                unsafe_allow_html=True)
    serie_reg = (df.groupby(["ano", "regiao"])["taxa_desemprego"]
                 .mean().reset_index())
    fig_reg = px.line(
        serie_reg, x="ano", y="taxa_desemprego",
        color="regiao", markers=True,
        labels={"ano": "Ano", "taxa_desemprego": "Taxa (%)", "regiao": "Região"},
    )
    fig_reg.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig_reg, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Renda Média × Inflação</div>',
                    unsafe_allow_html=True)
        fig_dual = go.Figure()
        fig_dual.add_trace(go.Bar(
            x=serie_ano["ano"], y=serie_ano["renda_media"],
            name="Renda Média (R$)", marker_color="#3b82f6", yaxis="y",
        ))
        fig_dual.add_trace(go.Scatter(
            x=serie_ano["ano"], y=serie_ano["inflacao"],
            name="Inflação (%)", mode="lines+markers",
            line=dict(color="#ef4444", width=2), yaxis="y2",
        ))
        fig_dual.update_layout(
            yaxis=dict(title="Renda Média (R$)"),
            yaxis2=dict(title="Inflação (%)", overlaying="y", side="right"),
            legend=dict(orientation="h", y=-0.2),
            margin=dict(t=20, b=40),
        )
        st.plotly_chart(fig_dual, width="stretch")

    with col2:
        st.markdown('<div class="section-title">Boxplot — Distribuição Trimestral</div>',
                    unsafe_allow_html=True)
        fig_box = px.box(
            df, x="trimestre", y="taxa_desemprego",
            color="trimestre",
            labels={"trimestre": "Trimestre", "taxa_desemprego": "Taxa (%)"},
        )
        fig_box.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig_box, width="stretch")

    st.markdown(
        '<div class="warning-box"><b>Atenção:</b> Os anos 2020 e 2021 '
        'registraram pico de desemprego associado à pandemia de COVID-19, '
        'superando a média histórica em ~1,4 pp.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ABA 3 — ANÁLISE REGIONAL / MAPA INTERATIVO
# ══════════════════════════════════════════════════════════════════════════════
with aba3:
    st.markdown('<div class="section-title">Mapa — Taxa de Desemprego por Estado</div>',
                unsafe_allow_html=True)

    # Mapa com coordenadas centrais dos estados (Plotly scatter_geo)
    uf_coords = {
        "AM": (-3.47, -65.10), "PA": (-3.41, -52.29), "RO": (-10.83, -62.84),
        "TO": (-10.25, -48.25), "BA": (-12.97, -41.73), "CE": (-5.20, -39.53),
        "PB": (-7.24, -36.78), "PE": (-8.38, -37.86), "MA": (-4.97, -45.27),
        "MG": (-18.51, -44.55), "RJ": (-22.25, -42.66), "SP": (-22.19, -48.79),
        "ES": (-19.57, -40.67), "PR": (-24.89, -51.55), "RS": (-30.17, -53.50),
        "SC": (-27.45, -50.95), "MS": (-20.51, -54.54), "MT": (-12.64, -55.42),
        "GO": (-15.98, -49.86), "DF": (-15.78, -47.93),
    }
    uf_df = (df.groupby("uf")["taxa_desemprego"].mean().reset_index())
    uf_df["lat"] = uf_df["uf"].map(lambda u: uf_coords.get(u, (0, 0))[0])
    uf_df["lon"] = uf_df["uf"].map(lambda u: uf_coords.get(u, (0, 0))[1])
    uf_df["taxa_desemprego"] = uf_df["taxa_desemprego"].round(2)

    fig_mapa = px.scatter_geo(
        uf_df, lat="lat", lon="lon",
        size="taxa_desemprego", color="taxa_desemprego",
        text="uf", hover_name="uf",
        hover_data={"taxa_desemprego": True, "lat": False, "lon": False},
        color_continuous_scale="RdYlGn_r",
        size_max=35,
        scope="south america",
        labels={"taxa_desemprego": "Taxa (%)"},
        title="Tamanho do círculo proporcional à taxa de desemprego",
    )
    fig_mapa.update_traces(textposition="top center")
    fig_mapa.update_geos(
        showcountries=True, countrycolor="gray",
        showcoastlines=True, coastlinecolor="gray",
        showland=True, landcolor="#f1f5f9",
        center=dict(lat=-15, lon=-55), projection_scale=2.8,
    )
    fig_mapa.update_layout(
        height=520,
        coloraxis_colorbar=dict(title="Taxa (%)"),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig_mapa, width="stretch")

    # Por região — barras empilhadas
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Taxa por Região</div>',
                    unsafe_allow_html=True)
        reg_df = (df.groupby("regiao")["taxa_desemprego"]
                  .mean().reset_index()
                  .sort_values("taxa_desemprego", ascending=False))
        fig_reg_bar = px.bar(
            reg_df, x="regiao", y="taxa_desemprego",
            text_auto=".1f", color="taxa_desemprego",
            color_continuous_scale="Reds",
            labels={"regiao": "Região", "taxa_desemprego": "Taxa Média (%)"},
        )
        fig_reg_bar.update_layout(coloraxis_showscale=False,
                                   margin=dict(t=20, b=20))
        st.plotly_chart(fig_reg_bar, width="stretch")

    with col2:
        st.markdown('<div class="section-title">Vagas Formais por Região</div>',
                    unsafe_allow_html=True)
        vagas_reg = (df.groupby("regiao")["vagas_formais"]
                     .sum().reset_index()
                     .sort_values("vagas_formais", ascending=False))
        fig_vagas = px.bar(
            vagas_reg, x="regiao", y="vagas_formais",
            text_auto=".2s", color="vagas_formais",
            color_continuous_scale="Blues",
            labels={"regiao": "Região", "vagas_formais": "Total de Vagas"},
        )
        fig_vagas.update_layout(coloraxis_showscale=False,
                                 margin=dict(t=20, b=20))
        st.plotly_chart(fig_vagas, width="stretch")

    st.markdown(
        '<div class="insight-box"><b>Insight regional:</b> O Sul concentra '
        'os menores índices de desemprego, puxado pelo agronegócio e setor industrial '
        'do RS, SC e PR. O Nordeste lidera negativamente, com CE e PB acima de 13%.</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ABA 4 — ANÁLISE SETORIAL
# ══════════════════════════════════════════════════════════════════════════════
with aba4:
    st.markdown('<div class="section-title">Desempenho por Setor Predominante</div>',
                unsafe_allow_html=True)

    setor_ano = (df.groupby(["ano", "setor_predominante"])["taxa_desemprego"]
                 .mean().reset_index())
    fig_setor_linha = px.line(
        setor_ano, x="ano", y="taxa_desemprego",
        color="setor_predominante", markers=True,
        labels={"ano": "Ano", "taxa_desemprego": "Taxa (%)",
                "setor_predominante": "Setor"},
    )
    fig_setor_linha.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig_setor_linha, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Renda Média por Setor</div>',
                    unsafe_allow_html=True)
        renda_setor = (df.groupby("setor_predominante")["renda_media"]
                       .mean().reset_index()
                       .sort_values("renda_media", ascending=False))
        fig_renda = px.bar(
            renda_setor, x="setor_predominante", y="renda_media",
            text_auto=",.0f", color="renda_media",
            color_continuous_scale="Greens",
            labels={"setor_predominante": "Setor", "renda_media": "Renda Média (R$)"},
        )
        fig_renda.update_layout(coloraxis_showscale=False,
                                 margin=dict(t=20, b=20))
        st.plotly_chart(fig_renda, width="stretch")

    with col2:
        st.markdown('<div class="section-title">Distribuição de Risco por Setor</div>',
                    unsafe_allow_html=True)
        risco_setor = (df.groupby(["setor_predominante", "nivel_risco"])
                       .size().reset_index(name="count"))
        fig_risco = px.bar(
            risco_setor, x="setor_predominante", y="count",
            color="nivel_risco",
            color_discrete_map={
                "Baixo": "#22c55e", "Médio": "#facc15",
                "Alto": "#f97316", "Crítico": "#ef4444",
            },
            labels={"setor_predominante": "Setor", "count": "Registros",
                    "nivel_risco": "Risco"},
            barmode="stack",
        )
        fig_risco.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig_risco, width="stretch")

    # Heatmap setor × região
    st.markdown('<div class="section-title">Heatmap — Taxa por Setor e Região</div>',
                unsafe_allow_html=True)
    pivot = (df.groupby(["regiao", "setor_predominante"])["taxa_desemprego"]
             .mean().reset_index()
             .pivot(index="regiao", columns="setor_predominante",
                    values="taxa_desemprego")
             .round(2))
    fig_heat = px.imshow(
        pivot, text_auto=True, color_continuous_scale="RdYlGn_r",
        labels=dict(x="Setor", y="Região", color="Taxa (%)"),
        aspect="auto",
    )
    fig_heat.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig_heat, width="stretch")


# ══════════════════════════════════════════════════════════════════════════════
# ABA 5 — CORRELAÇÕES ESTATÍSTICAS (funcionalidade avançada)
# ══════════════════════════════════════════════════════════════════════════════
with aba5:
    st.markdown('<div class="section-title">Análise de Correlações Estatísticas</div>',
                unsafe_allow_html=True)

    numericas = ["taxa_desemprego", "renda_media", "populacao_ativa",
                 "empregados", "desempregados", "vagas_formais", "inflacao"]
    corr = df[numericas].corr().round(2)

    fig_corr = px.imshow(
        corr, text_auto=True, color_continuous_scale="RdBu",
        color_continuous_midpoint=0, zmin=-1, zmax=1,
        title="Matriz de Correlação de Pearson",
        labels=dict(color="r"),
        aspect="auto",
    )
    fig_corr.update_layout(height=500, margin=dict(t=50, b=20))
    st.plotly_chart(fig_corr, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Taxa de Desemprego × Inflação</div>',
                    unsafe_allow_html=True)
        fig_sc1 = px.scatter(
            df, x="inflacao", y="taxa_desemprego",
            color="regiao", trendline="ols", opacity=0.6,
            labels={"inflacao": "Inflação (%)",
                    "taxa_desemprego": "Taxa de Desemprego (%)"},
        )
        fig_sc1.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig_sc1, width="stretch")

    with col2:
        st.markdown('<div class="section-title">Renda Média × Vagas Formais</div>',
                    unsafe_allow_html=True)
        fig_sc2 = px.scatter(
            df, x="vagas_formais", y="renda_media",
            color="nivel_risco",
            color_discrete_map={
                "Baixo": "#22c55e", "Médio": "#facc15",
                "Alto": "#f97316", "Crítico": "#ef4444",
            },
            trendline="ols", opacity=0.6,
            labels={"vagas_formais": "Vagas Formais",
                    "renda_media": "Renda Média (R$)"},
        )
        fig_sc2.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig_sc2, width="stretch")

    # Insight estatístico calculado
    r_desemp_infl = df["taxa_desemprego"].corr(df["inflacao"])
    r_renda_vagas = df["renda_media"].corr(df["vagas_formais"])

    st.markdown(
        f'<div class="insight-box"><b>Coeficientes de correlação:</b><br>'
        f'• Taxa de desemprego × Inflação: <b>r = {r_desemp_infl:.3f}</b> '
        f'({"fraca" if abs(r_desemp_infl) < 0.3 else "moderada" if abs(r_desemp_infl) < 0.7 else "forte"})<br>'
        f'• Renda média × Vagas formais: <b>r = {r_renda_vagas:.3f}</b> '
        f'({"fraca" if abs(r_renda_vagas) < 0.3 else "moderada" if abs(r_renda_vagas) < 0.7 else "forte"})'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Conclusão executiva
    st.divider()
    st.markdown("### Conclusão Executiva")
    st.markdown("""
O presente dashboard demonstra uma análise abrangente do mercado de trabalho brasileiro
entre 2015 e 2024, revelando padrões críticos que impactam decisões de política pública:

1. **Concentração regional**: O Nordeste responde pela maior parcela de desemprego
   estrutural, enquanto o Sul mantém os menores índices do país.
2. **Impacto da pandemia**: Os anos 2020–2021 representaram o maior choque de
   desemprego do período analisado, superando 11% em média nacional.
3. **Setorial**: A Construção Civil lidera os percentuais de desemprego setorial,
   enquanto Serviços sustentam renda média superior.
4. **Vagas formais**: Sul e Centro-Oeste mostram maior geração de empregos formais
   per capita, reforçando seu papel como motores econômicos regionais.
5. **Correlação inflação-desemprego**: A correlação fraca entre inflação e
   desemprego indica que outros vetores — como ciclos políticos e choques externos —
   são determinantes mais relevantes no contexto nacional.
""")
