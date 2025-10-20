import streamlit as st
import pandas as pd
import plotly.express as px
from pages.utils.data_loader import get_data

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================
st.title("🧩 Análise por Assunto")

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
subjects = st.sidebar.multiselect("Assunto", sorted(df["subject"].dropna().unique()))
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
if subjects:
    df_filtered = df_filtered[df_filtered["subject"].isin(subjects)]

df_filtered = df_filtered[
    (df_filtered["date"] >= pd.to_datetime(start_date))
    & (df_filtered["date"] <= pd.to_datetime(end_date))
]

# ==========================================================
# AGREGAÇÃO E CÁLCULOS
# ==========================================================
df_subject = df_filtered.groupby(["topic", "subject"], as_index=False).agg(
    sessions_total=("sessions_total", "sum"),
    session_retained=("session_retained", "sum"),
    sessions_human_assistance=("sessions_human_assistance", "sum"),
)
df_subject["retention_rate"] = (
    df_subject["session_retained"] / df_subject["sessions_total"]
)
df_subject["human_request_rate"] = (
    df_subject["sessions_human_assistance"] / df_subject["sessions_total"]
)
df_subject["efficiency_score"] = (
    df_subject["retention_rate"] - df_subject["human_request_rate"]
)

# ==========================================================
# GRÁFICOS
# ==========================================================
st.subheader("📊 Volume e Eficiência por Assunto")

# Top 10 assuntos com maior volume
top_subjects = df_subject.sort_values("sessions_total", ascending=False).head(10)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        top_subjects.sort_values("sessions_total", ascending=True),
        x="sessions_total",
        y="subject",
        orientation="h",
        title="Assuntos com maior volume de sessões",
        labels={"sessions_total": "Sessões Totais", "subject": "Assunto"},
        color="sessions_total",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(
        top_subjects.sort_values("efficiency_score", ascending=True),
        x="efficiency_score",
        y="subject",
        orientation="h",
        title="Eficiência (retenção - pedido humano)",
        labels={"efficiency_score": "Eficiência", "subject": "Assunto"},
        color="efficiency_score",
        color_continuous_scale="RdYlGn",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ==========================================================
# EVOLUÇÃO TEMPORAL POR ASSUNTO (opcional)
# ==========================================================
if subjects:
    st.subheader("📈 Evolução Temporal dos Assuntos Selecionados")
    df_time = (
        df_filtered.groupby(["date", "subject"], as_index=False)
        .agg(sessions_total=("sessions_total", "sum"))
        .sort_values("date")
    )
    if enable_smoothing:
        df_time["sessions_total"] = df_time.groupby("subject")[
            "sessions_total"
        ].transform(lambda x: x.rolling(7, min_periods=1).mean())

    fig_time = px.line(
        df_time,
        x="date",
        y="sessions_total",
        color="subject",
        title="Evolução de Sessões ao longo do tempo (por assunto selecionado)",
        labels={"sessions_total": "Sessões Totais", "date": "Data"},
        markers=True,
    )
    st.plotly_chart(fig_time, use_container_width=True)

# ==========================================================
# TABELA DE RESUMO
# ==========================================================
st.subheader("📋 Resumo de Assuntos")
st.dataframe(
    df_subject.sort_values("sessions_total", ascending=False).style.format(
        {
            "sessions_total": "{:,.0f}",
            "retention_rate": "{:.1%}",
            "human_request_rate": "{:.1%}",
            "efficiency_score": "{:.1%}",
        }
    ),
    use_container_width=True,
)
