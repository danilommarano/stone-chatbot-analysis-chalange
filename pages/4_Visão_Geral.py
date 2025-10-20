import streamlit as st
import pandas as pd
from pages.utils.charts import daily_sessions_chart, retention_rate_chart
from pages.utils.data_loader import get_data

st.title("📊 Visão Geral")

df = get_data()  # garante que o dataframe está disponível

# ==========================================================
# FILTROS
# ==========================================================
st.sidebar.header("Filtros")

min_date = df["date"].min()
max_date = df["date"].max()

# --- Filtro de Data com tratamento seguro ---
date_selection = st.sidebar.date_input(
    "Selecione o intervalo",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Corrige o caso em que o usuário seleciona apenas uma data
if isinstance(date_selection, tuple) and len(date_selection) == 2:
    start_date, end_date = date_selection
else:
    start_date = end_date = date_selection

# --- Outros filtros ---
bots = st.sidebar.multiselect("Bot", sorted(df["bot"].dropna().unique()))
techs = st.sidebar.multiselect("Tech", sorted(df["tech"].dropna().unique()))
fonts = st.sidebar.multiselect("Fonte", sorted(df["font"].dropna().unique()))

# --- Toggle para média móvel ---
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

df_filtered = df_filtered[
    (df_filtered["date"] >= pd.to_datetime(start_date))
    & (df_filtered["date"] <= pd.to_datetime(end_date))
]

# ==========================================================
# AGREGAÇÃO E MÉTRICAS
# ==========================================================
df_daily = df_filtered.groupby("date", as_index=False).agg(
    sessions_total=("sessions_total", "sum"),
    session_retained=("session_retained", "sum"),
    sessions_human_assistance=("sessions_human_assistance", "sum"),
)
df_daily["retention_rate"] = df_daily["session_retained"] / df_daily["sessions_total"]
df_daily["human_request_rate"] = (
    df_daily["sessions_human_assistance"] / df_daily["sessions_total"]
)

# ==========================================================
# KPIs
# ==========================================================
col1, col2, col3 = st.columns(3)
col1.metric(
    "Total de Sessões", f"{df_daily['sessions_total'].sum():,}".replace(",", ".")
)
col2.metric("Taxa de Retenção Média", f"{df_daily['retention_rate'].mean():.1%}")
col3.metric(
    "Taxa de Pedido Humano Média", f"{df_daily['human_request_rate'].mean():.1%}"
)

# ==========================================================
# GRÁFICOS
# ==========================================================
st.plotly_chart(
    daily_sessions_chart(df_daily, enable_smoothing), use_container_width=True
)
st.plotly_chart(
    retention_rate_chart(df_daily, enable_smoothing), use_container_width=True
)
