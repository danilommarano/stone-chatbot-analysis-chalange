import streamlit as st
import pandas as pd
import plotly.express as px
from pages.utils.data_loader import get_data

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================
st.title("🔻 Funil de Atendimento")

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
fonts = st.sidebar.multiselect("Fonte (Canal)", sorted(df["font"].dropna().unique()))
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
# AGREGAÇÃO GERAL DO FUNIL
# ==========================================================
# soma global das métricas principais
funnel_df = pd.DataFrame(
    {
        "sessions_total": [df_filtered["sessions_total"].sum()],
        "session_retained": [df_filtered["session_retained"].sum()],
        "sessions_human_assistance": [df_filtered["sessions_human_assistance"].sum()],
    }
)

# Cálculo de perdas (sessões não resolvidas)
funnel_df["loss_count"] = funnel_df["sessions_total"] - funnel_df["session_retained"]
funnel_df["loss_count"] = funnel_df["loss_count"].apply(lambda x: x if x > 0 else 0)

# Cálculo das taxas
funnel_df["retention_rate"] = (
    funnel_df["session_retained"] / funnel_df["sessions_total"]
)
funnel_df["human_request_rate"] = (
    funnel_df["sessions_human_assistance"] / funnel_df["sessions_total"]
)
funnel_df["loss_rate"] = funnel_df["loss_count"] / funnel_df["sessions_total"]

# Extrair valores finais
total_sessions = funnel_df.loc[0, "sessions_total"]
retained = funnel_df.loc[0, "session_retained"]
human = funnel_df.loc[0, "sessions_human_assistance"]
loss = funnel_df.loc[0, "loss_count"]

retention_rate = funnel_df.loc[0, "retention_rate"]
human_request_rate = funnel_df.loc[0, "human_request_rate"]
loss_rate = funnel_df.loc[0, "loss_rate"]

# Montar DataFrame do funil (3 etapas)
funnel_data = pd.DataFrame(
    {
        "Etapa": ["Sessões Totais", "Sessões Retidas", "Sessões Não Resolvidas"],
        "Quantidade": [total_sessions, retained, loss],
    }
)

# ==========================================================
# GRÁFICO DE FUNIL
# ==========================================================
st.subheader("📊 Estrutura do Funil de Atendimento")

fig_funnel = px.funnel(
    funnel_data,
    x="Quantidade",
    y="Etapa",
    color="Etapa",
    color_discrete_sequence=["#1f77b4", "#2ca02c", "#d62728"],
    title="Fluxo de Sessões: Totais → Retidas → Não Resolvidas",
)
st.plotly_chart(fig_funnel, use_container_width=True)

# ==========================================================
# KPIs PRINCIPAIS
# ==========================================================
st.subheader("📈 Indicadores de Conversão")

col1, col2, col3 = st.columns(3)
col1.metric("Total de Sessões", f"{total_sessions:,.0f}".replace(",", "."))
col2.metric("Taxa de Retenção", f"{retention_rate:.1%}")
col3.metric("Taxa de Sessões Não Resolvidas", f"{loss_rate:.1%}")

# ==========================================================
# EVOLUÇÃO TEMPORAL DO FUNIL
# ==========================================================
st.subheader("🕒 Evolução Temporal — Retenção x Não Resolvidas")

df_daily = df_filtered.groupby("date", as_index=False).agg(
    sessions_total=("sessions_total", "sum"),
    session_retained=("session_retained", "sum"),
)
df_daily["loss_count"] = df_daily["sessions_total"] - df_daily["session_retained"]
df_daily["retention_rate"] = df_daily["session_retained"] / df_daily["sessions_total"]
df_daily["loss_rate"] = df_daily["loss_count"] / df_daily["sessions_total"]

if enable_smoothing:
    df_daily[["retention_rate", "loss_rate"]] = (
        df_daily[["retention_rate", "loss_rate"]].rolling(7, min_periods=1).mean()
    )

fig_time = px.line(
    df_daily,
    x="date",
    y=["retention_rate", "loss_rate"],
    labels={"value": "Taxa", "variable": "Indicador", "date": "Data"},
    color_discrete_map={
        "retention_rate": "#2ca02c",
        "loss_rate": "#d62728",
    },
    title="Tendência das Taxas de Retenção e Sessões Não Resolvidas ao Longo do Tempo",
)
fig_time.update_layout(yaxis_tickformat=".0%")
st.plotly_chart(fig_time, use_container_width=True)

# ==========================================================
# TABELA DE DETALHAMENTO
# ==========================================================
st.subheader("📋 Detalhamento Diário do Funil")

st.dataframe(
    df_daily.sort_values("date", ascending=False).style.format(
        {
            "sessions_total": "{:,.0f}",
            "session_retained": "{:,.0f}",
            "loss_count": "{:,.0f}",
            "retention_rate": "{:.1%}",
            "loss_rate": "{:.1%}",
        }
    ),
    use_container_width=True,
)
