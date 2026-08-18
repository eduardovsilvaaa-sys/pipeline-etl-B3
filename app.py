import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine

# Configuração do Streamlit
st.set_page_config(
    page_title="B3 Market Intelligence | Dashboard",
    page_icon="📈",
    layout="wide",
)

st.markdown(
    """
    <style>
        .main { background-color: #0e1117; }
        .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; border: 1px solid #2e3545; }
    </style>
""",
    unsafe_allow_html=True,
)

@st.cache_data(ttl=60)
def carregar_dados():
    db_url = "postgresql://admin:senha123@localhost:5432/acoes"
    engine = create_engine(db_url)
    query = """
        SELECT 
            ativo,
            nome_empresa,
            preco_atual,
            variacao_pct,
            maxima_dia,
            minima_dia,
            preco_fechamento_anterior,
            volume_negociado,
            data_hora_coleta AS data_consulta
        FROM fato_cotacoes
        ORDER BY data_consulta DESC
    """
    df = pd.read_sql(query, con=engine)

    if not df.empty:
        # Pega apenas a cotação mais recente de cada ativo
        df_latest = df.sort_values("data_consulta").groupby("ativo").last().reset_index()

        # Cálculo de Amplitude Diária (Volatilidade em R$)
        df_latest["amplitude_dia"] = (
            df_latest["maxima_dia"] - df_latest["minima_dia"]
        )

        # % do preço atual em relação ao topo do dia
        df_latest["pct_da_maxima"] = (
            df_latest["preco_atual"] / df_latest["maxima_dia"]
        ) * 100

        return df_latest
    return pd.DataFrame()


df = carregar_dados()

# 3. Cabeçalho Principal
st.title("📈 B3 Market Intelligence — Camada Gold")
st.caption("Dados extraídos da API, processados via Parquet (Silver) e carregados no PostgreSQL.")

if df.empty:
    st.warning("Nenhum dado encontrado no PostgreSQL. Execute o `python main.py` primeiro.")
    st.stop()

# 4. Barra Lateral com Filtros
st.sidebar.header("🔍 Filtros de Mercado")
ativos_selecionados = st.sidebar.multiselect(
    "Selecione os Ativos:",
    options=df["ativo"].unique(),
    default=df["ativo"].unique(),
)

df_filtrado = df[df["ativo"].isin(ativos_selecionados)]

# 5. Cards de Métricas Principais (KPIs)
col1, col2, col3, col4 = st.columns(4)

total_volume = df_filtrado["volume_negociado"].sum()
maior_alta = df_filtrado.loc[df_filtrado["variacao_pct"].idxmax()]
maior_baixa = df_filtrado.loc[df_filtrado["variacao_pct"].idxmin()]

with col1:
    st.metric("Total de Ativos Monitorados", len(df_filtrado))

with col2:
    st.metric(
        "Volume Total Negociado",
        f"R$ {total_volume:,.0f}".replace(",", "."),
    )

with col3:
    st.metric(
        f"Destaque de Alta ({maior_alta['ativo']})",
        f"R$ {maior_alta['preco_atual']:.2f}",
        delta=f"{maior_alta['variacao_pct']:.2f}%",
    )

with col4:
    st.metric(
        f"Destaque de Baixa ({maior_baixa['ativo']})",
        f"R$ {maior_baixa['preco_atual']:.2f}",
        delta=f"{maior_baixa['variacao_pct']:.2f}%",
    )

st.markdown("---")

# 6. Gráficos Analíticos de Nível Profissional
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📊 Performance Diária (%)")
    fig_var = px.bar(
        df_filtrado,
        x="ativo",
        y="variacao_pct",
        color="variacao_pct",
        color_continuous_scale=["#ef5350", "#26a69a"],
        text_auto=".2f",
        labels={"variacao_pct": "Variação (%)", "ativo": "Ativo"},
    )
    fig_var.update_layout(
        template="plotly_dark", showlegend=False, height=380
    )
    st.plotly_chart(fig_var, use_container_width=True)

with col_graf2:
    st.subheader("💰 Liquidez de Mercado (Volume Negociado)")
    fig_vol = px.pie(
        df_filtrado,
        names="ativo",
        values="volume_negociado",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_vol.update_layout(template="plotly_dark", height=380)
    st.plotly_chart(fig_vol, use_container_width=True)

# 7. Gráfico de Amplitude Ticker a Ticker (Máxima vs Mínima vs Atual)
st.subheader("📌 Faixa de Negociação do Dia (Mínima / Atual / Máxima)")

fig_range = go.Figure()

for _, row in df_filtrado.iterrows():
    fig_range.add_trace(
        go.Scatter(
            x=[row["minima_dia"], row["preco_atual"], row["maxima_dia"]],
            y=[row["ativo"], row["ativo"], row["ativo"]],
            mode="lines+markers",
            name=row["ativo"],
            marker=dict(size=[10, 16, 10], color=["#ef5350", "#29b6f6", "#26a69a"]),
            line=dict(color="#546e7a", width=3),
        )
    )

fig_range.update_layout(
    template="plotly_dark",
    xaxis_title="Preço (R$)",
    yaxis_title="Ativo",
    height=300,
    showlegend=False,
)
st.plotly_chart(fig_range, use_container_width=True)

# 8. Tabela Completa do Data Lake
with st.expander("📋 Visualizar Tabela Bruta (Camada Gold)"):
    st.dataframe(df_filtrado, use_container_width=True)