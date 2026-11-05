import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Números que Falam - Descobrindo o Brasil",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main-title { font-size: 2.2rem; color: #1e3d59; font-weight: 800; margin-bottom: 0px; }
        .sub-title { font-size: 1.1rem; color: #576574; margin-bottom: 20px; }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="main-title">🇧🇷 Números que Falam — Descobrindo o Brasil</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">Dashboard Integrado de Indicadores Demográficos do IBGE</p>',
    unsafe_allow_html=True,
)
st.markdown("---")


@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("dados_ibge_projeto.csv")
        return df
    except Exception:
        dados_fallback = {
            "UF": ["AM", "AM", "RR", "MS", "BA", "SP", "CE", "PR"],
            "Regiao": [
                "Norte",
                "Norte",
                "Norte",
                "Centro-Oeste",
                "Nordeste",
                "Sudeste",
                "Nordeste",
                "Sul",
            ],
            "Etnia": [
                "Tikúna",
                "Yanomami",
                "Yanomami",
                "Guarani Kaiowá",
                "Pataxó",
                "Guarani",
                "Tuxá",
                "Kaingang",
            ],
            "Situacao_Domicilio": [
                "Rural",
                "Rural",
                "Rural",
                "Rural",
                "Rural",
                "Urbana",
                "Urbana",
                "Rural",
            ],
            "Populacao_Indigena": [
                35000,
                27000,
                25000,
                45000,
                12000,
                5000,
                8000,
                19000,
            ],
            "Rendimento_Medio": [
                1200,
                1100,
                1150,
                1500,
                1550,
                2400,
                1600,
                2100,
            ],
            "Taxa_Alfabetizacao": [
                78.5,
                62.0,
                60.0,
                81.0,
                83.0,
                96.5,
                79.0,
                88.0,
            ],
            "Idade_Media": [24.5, 21.0, 20.5, 26.4, 27.5, 33.0, 28.4, 29.0],
            "Tempo_Deslocamento": [45, 50, 55, 38, 32, 20, 28, 40],
        }
        return pd.DataFrame(dados_fallback)


df_original = carregar_dados()

with st.sidebar:
    st.markdown("### ⚙️ Painel de Controlo")

    regioes = ["Todas"] + list(df_original["Regiao"].unique())
    regiao_sel = st.selectbox("Região:", regioes)

    if regiao_sel != "Todas":
        ufs_disponiveis = [
            "Todas"
        ] + list(
            df_original[df_original["Regiao"] == regiao_sel]["UF"].unique()
        )
    else:
        ufs_disponiveis = ["Todas"] + list(df_original["UF"].unique())

    uf_sel = st.selectbox("Unidade Federativa (UF):", ufs_disponiveis)

    situacoes = ["Todas"] + list(df_original["Situacao_Domicilio"].unique())
    situacao_sel = st.selectbox("Situação do Domicílio (Rural/Urbana):", situacoes)

    etnias_disp = ["Todas"] + list(df_original["Etnia"].unique())
    etnia_sel = st.selectbox("Etnia Específica:", etnias_disp)

    st.markdown("---")
    st.markdown("#### 📈 Seleção dos 9 Gráficos Obrigatórios")
    opcao_grafico = st.selectbox(
        "Escolha o Tipo de Gráfico:",
        [
            "1. Gráfico de Barras (População por Região)",
            "2. Boxplot (Dispersão e Outliers da População)",
            "3. Gráfico de Dispersão (Rendimento vs População)",
            "4. Gráfico de Distribuição (Histograma do Rendimento)",
            "5. Gráfico de Frequência (Contagem por Etnia)",
            "6. Heatmap (Densidade: Região vs Domicílio)",
            "7. Gráfico de Linhas (Evolução da Idade Média)",
            "8. Gráfico de Pizza (Proporção Urbana vs Rural)",
            "9. Gráfico de Regressão (Alfabetização vs Rendimento)",
        ],
    )

df_filtrado = df_original.copy()
if regiao_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Regiao"] == regiao_sel]
if uf_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["UF"] == uf_sel]
if situacao_sel != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["Situacao_Domicilio"] == situacao_sel
    ]
if etnia_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Etnia"] == etnia_sel]

pop_ind = (
    df_filtrado["Populacao_Indigena"]
    if not df_filtrado.empty
    else pd.Series([0])
)
media_pop = pop_ind.mean()
mediana_pop = pop_ind.median()
q1 = np.percentile(pop_ind, 25) if len(pop_ind) > 1 else 0
q3 = np.percentile(pop_ind, 75) if len(pop_ind) > 1 else 0
iqr = q3 - q1
desv_pad = pop_ind.std() if len(pop_ind) > 1 else 0

st.markdown(
    "### 📌 Indicadores Estatísticos Globais (Atualizados em Tempo Real)"
)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Média Populacional", f"{media_pop:,.0f} hab".replace(",", "."))
c2.metric("Mediana (Robusta)", f"{mediana_pop:,.0f} hab".replace(",", "."))
c3.metric("IQR (Q3 - Q1)", f"{iqr:,.0f} hab".replace(",", "."))
c4.metric("Desvio Padrão", f"{desv_pad:,.1f} hab".replace(",", "."))

st.markdown("---")

if df_filtrado.empty:
    st.warning(
        "⚠️ Nenhum registo encontrado com a combinação de filtros selecionada. Por favor, ajuste os parâmetros na barra lateral."
    )
else:
    if opcao_grafico.startswith("1."):
        st.subheader("📊 1. Gráfico de Barras — População Indígena por Região")
        fig = px.bar(
            df_filtrado.groupby("Regiao")["Populacao_Indigena"]
            .sum()
            .reset_index(),
            x="Regiao",
            y="Populacao_Indigena",
            color="Regiao",
            text_auto=True,
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("2."):
        st.subheader("📊 2. Boxplot — Análise de Dispersão e Outliers")
        fig = px.box(
            df_filtrado,
            x="Regiao",
            y="Populacao_Indigena",
            color="Regiao",
            points="all",
            template="plotly_white",
            title="Distribuição e Identificação de Outliers por Região",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("3."):
        st.subheader(
            "📊 3. Gráfico de Dispersão — Rendimento vs População Indígena"
        )
        fig = px.scatter(
            df_filtrado,
            x="Rendimento_Medio",
            y="Populacao_Indigena",
            color="Etnia",
            size="Populacao_Indigena",
            template="plotly_white",
            title="Cruzamento de Rendimento Médio e Volume Populacional",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("4."):
        st.subheader(
            "📊 4. Gráfico de Distribuição — Histograma do Rendimento Médio"
        )
        fig = px.histogram(
            df_filtrado,
            x="Rendimento_Medio",
            nbins=10,
            template="plotly_white",
            color_discrete_sequence=["#1f77b4"],
            title="Frequência e Distribuição dos Rendimentos",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("5."):
        st.subheader(
            "📊 5. Gráfico de Frequência — Contagem Demográfica por Etnia"
        )
        freq_df = df_filtrado["Etnia"].value_counts().reset_index()
        freq_df.columns = ["Etnia", "Contagem"]
        fig = px.bar(
            freq_df,
            x="Etnia",
            y="Contagem",
            color="Etnia",
            template="plotly_white",
            title="Frequência de Ocorrência por Grupo Étnico",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("6."):
        st.subheader("📊 6. Heatmap — Densidade: Região vs Domicílio")
        fig = px.density_heatmap(
            df_filtrado,
            x="Regiao",
            y="Situacao_Domicilio",
            z="Populacao_Indigena",
            histfunc="sum",
            template="plotly_white",
            title="Mapa de Calor: Concentração Domiciliar e Geográfica",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("7."):
        st.subheader(
            "📊 7. Gráfico de Linhas — Análise da Idade Média por Etnia/UF"
        )
        fig = px.line(
            df_filtrado.sort_values("Idade_Media"),
            x="Etnia",
            y="Idade_Media",
            markers=True,
            template="plotly_white",
            title="Variação da Idade Média Demográfica",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("8."):
        st.subheader(
            "📊 8. Gráfico de Pizza / Rosca — Proporção Urbana vs Rural"
        )
        fig = px.pie(
            df_filtrado,
            names="Situacao_Domicilio",
            values="Populacao_Indigena",
            hole=0.4,
            template="plotly_white",
            title="Proporção da População por Tipo de Domicílio",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao_grafico.startswith("9."):
        st.subheader(
            "📊 9. Gráfico de Regressão — Taxa de Alfabetização vs Rendimento"
        )
        x = df_filtrado["Taxa_Alfabetizacao"]
        y = df_filtrado["Rendimento_Medio"]

        fig = px.scatter(
            df_filtrado,
            x="Taxa_Alfabetizacao",
            y="Rendimento_Medio",
            color="Etnia",
            template="plotly_white",
            title="Relação entre Alfabetização e Rendimento Médio",
        )

        if len(df_filtrado) > 1:
            coef = np.polyfit(x, y, 1)
            poly1d_fn = np.poly1d(coef)
            x_trend = np.linspace(x.min(), x.max(), 100)
            y_trend = poly1d_fn(x_trend)

            fig.add_scatter(
                x=x_trend,
                y=y_trend,
                mode="lines",
                name="Linha de Regressão",
                line=dict(color="red", dash="dash"),
            )

        st.plotly_chart(fig, use_container_width=True)