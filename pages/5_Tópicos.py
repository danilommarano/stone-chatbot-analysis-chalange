import streamlit as st
import pandas as pd
import plotly.express as px
from pages.utils.data_loader import get_data

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================
st.title("🎯 Análise por Tópico e Assunto")

df = get_data()

# ==========================================================
# FILTROS
# ==========================================================
st.sidebar.header("Filtros")

min_date = df["date"].min()
max_date = df["date"].max()

# --- Filtro de Data com fallback seguro ---
date_selection = st.sidebar.date_input(
    "Selecione o intervalo",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_selection, tuple) and len(date_selection) == 2:
    start_date, end_date = date_selection
else:
    start_date = end_date = date_selection

bots = st.sidebar.multiselect("Bot", sorted(df["bot"].dropna().unique()))
techs = st.sidebar.multiselect("Tech", sorted(df["tech"].dropna().unique()))
fonts = st.sidebar.multiselect("Fonte", sorted(df["font"].dropna().unique()))
topics = st.sidebar.multiselect("Tópico", sorted(df["topic"].dropna().unique()))
enable_smoothing = st.sidebar.toggle("📈 Média móvel 7 dias", value=False)

# ==========================================================
# APLICAR FILTROS
# ==========================================================
df_filtered = df.copy()

if bots:
    df_filtered = df_filtered[df_filtered["bot"].isin(bots)]
if techs:
    df_filtered = df_filtered[df_filtered["tech"].isin(techs)]
if fonts:
    df_filtered = df_filtered[df_filtered["font"].isin(fonts)]
if topics:
    df_filtered = df_filtered[df_filtered["topic"].isin(topics)]

df_filtered = df_filtered[
    (df_filtered["date"] >= pd.to_datetime(start_date))
    & (df_filtered["date"] <= pd.to_datetime(end_date))
]

# ==========================================================
# AGREGAÇÃO E CÁLCULOS
# ==========================================================
df_topic = df_filtered.groupby("topic", as_index=False).agg(
    sessions_total=("sessions_total", "sum"),
    session_retained=("session_retained", "sum"),
    sessions_human_assistance=("sessions_human_assistance", "sum"),
)
df_topic["retention_rate"] = df_topic["session_retained"] / df_topic["sessions_total"]
df_topic["human_request_rate"] = (
    df_topic["sessions_human_assistance"] / df_topic["sessions_total"]
)

# ==========================================================
# GRÁFICOS
# ==========================================================
st.subheader("📊 Volume e Eficiência por Tópico")

# Top 10 tópicos com maior volume
top_topics = df_topic.sort_values("sessions_total", ascending=False).head(10)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        top_topics.sort_values("sessions_total", ascending=True),
        x="sessions_total",
        y="topic",
        orientation="h",
        title="Tópicos com maior volume de sessões",
        labels={"sessions_total": "Sessões Totais", "topic": "Tópico"},
        color="sessions_total",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(
        top_topics.sort_values("retention_rate", ascending=True),
        x="retention_rate",
        y="topic",
        orientation="h",
        title="Taxa de Retenção por Tópico (Top 10 por volume)",
        labels={"retention_rate": "Taxa de Retenção", "topic": "Tópico"},
        color="retention_rate",
        color_continuous_scale="Greens",
    )
    fig2.update_layout(xaxis_tickformat=".0%")
    st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
# EVOLUÇÃO TEMPORAL POR TÓPICO (opcional)
# ==========================================================
if topics:
    st.subheader("📈 Evolução Temporal dos Tópicos Selecionados")
    df_time = (
        df_filtered.groupby(["date", "topic"], as_index=False)
        .agg(sessions_total=("sessions_total", "sum"))
        .sort_values("date")
    )
    if enable_smoothing:
        df_time["sessions_total"] = df_time.groupby("topic")[
            "sessions_total"
        ].transform(lambda x: x.rolling(7, min_periods=1).mean())

    fig_time = px.line(
        df_time,
        x="date",
        y="sessions_total",
        color="topic",
        title="Evolução de Sessões ao longo do tempo (por tópico selecionado)",
        labels={"sessions_total": "Sessões Totais", "date": "Data"},
        markers=True,
    )
    st.plotly_chart(fig_time, use_container_width=True)

# ==========================================================
# TABELA DE RESUMO
# ==========================================================
st.subheader("📋 Resumo de Tópicos")

st.dataframe(
    df_topic.sort_values("sessions_total", ascending=False).style.format(
        {
            "sessions_total": "{:,.0f}",
            "retention_rate": "{:.1%}",
            "human_request_rate": "{:.1%}",
        }
    ),
    use_container_width=True,
)
