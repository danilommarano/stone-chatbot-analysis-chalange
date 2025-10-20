import streamlit as st
import pandas as pd
import plotly.express as px
from pages.utils.data_loader import get_data

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================
st.title("⚙️ Comparativo entre Bots, Tecnologias e Canais")

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
# AGREGAÇÃO E MÉTRICAS GERAIS
# ==========================================================
def aggregate_by(column):
    df_grouped = df_filtered.groupby(column, as_index=False).agg(
        sessions_total=("sessions_total", "sum"),
        session_retained=("session_retained", "sum"),
        sessions_human_assistance=("sessions_human_assistance", "sum"),
    )
    df_grouped["retention_rate"] = (
        df_grouped["session_retained"] / df_grouped["sessions_total"]
    )
    df_grouped["human_request_rate"] = (
        df_grouped["sessions_human_assistance"] / df_grouped["sessions_total"]
    )
    df_grouped["efficiency_score"] = (
        df_grouped["retention_rate"] - df_grouped["human_request_rate"]
    )
    return df_grouped


df_bot = aggregate_by("bot")
df_tech = aggregate_by("tech")
df_font = aggregate_by("font")

# ==========================================================
# VISUALIZAÇÕES — VOLUME E EFICIÊNCIA
# ==========================================================
st.subheader("📊 Comparativo de Volume e Eficiência")

col1, col2, col3 = st.columns(3)

# --- Bots ---
with col1:
    fig_bot = px.bar(
        df_bot.sort_values("sessions_total", ascending=False),
        x="sessions_total",
        y="bot",
        orientation="h",
        color="efficiency_score",
        color_continuous_scale="RdYlGn",
        title="Bots — Volume e Eficiência",
        labels={
            "sessions_total": "Sessões Totais",
            "bot": "Bot",
            "efficiency_score": "Eficiência",
        },
    )
    st.plotly_chart(fig_bot, use_container_width=True)

# --- Tecnologias ---
with col2:
    fig_tech = px.bar(
        df_tech.sort_values("sessions_total", ascending=False),
        x="sessions_total",
        y="tech",
        orientation="h",
        color="efficiency_score",
        color_continuous_scale="RdYlGn",
        title="Tecnologias — Volume e Eficiência",
        labels={
            "sessions_total": "Sessões Totais",
            "tech": "Tecnologia",
            "efficiency_score": "Eficiência",
        },
    )
    st.plotly_chart(fig_tech, use_container_width=True)

# --- Fontes ---
with col3:
    fig_font = px.bar(
        df_font.sort_values("sessions_total", ascending=False),
        x="sessions_total",
        y="font",
        orientation="h",
        color="efficiency_score",
        color_continuous_scale="RdYlGn",
        title="Canais — Volume e Eficiência",
        labels={
            "sessions_total": "Sessões Totais",
            "font": "Fonte",
            "efficiency_score": "Eficiência",
        },
    )
    st.plotly_chart(fig_font, use_container_width=True)

# ==========================================================
# MATRIZ DE DESEMPENHO
# ==========================================================
st.subheader("📈 Matriz de Desempenho (Volume x Retenção x Pedido Humano)")

df_perf = pd.concat(
    [
        df_bot.assign(level="Bot", label=df_bot["bot"]),
        df_tech.assign(level="Tech", label=df_tech["tech"]),
        df_font.assign(level="Fonte", label=df_font["font"]),
    ],
    ignore_index=True,
)

fig_perf = px.scatter(
    df_perf,
    x="sessions_total",
    y="retention_rate",
    color="level",
    size="sessions_total",
    hover_data=["label", "human_request_rate", "efficiency_score"],
    title="Comparativo Geral — Volume x Retenção (Cor = Categoria)",
    labels={
        "sessions_total": "Sessões Totais",
        "retention_rate": "Taxa de Retenção",
        "level": "Categoria",
    },
)
fig_perf.update_layout(yaxis_tickformat=".0%")
st.plotly_chart(fig_perf, use_container_width=True)

# ==========================================================
# TABELAS DE RESUMO
# ==========================================================
st.subheader("📋 Resumo por Categoria")

tabs = st.tabs(["Bots", "Tecnologias", "Canais"])

with tabs[0]:
    st.dataframe(
        df_bot.sort_values("sessions_total", ascending=False).style.format(
            {
                "sessions_total": "{:,.0f}",
                "retention_rate": "{:.1%}",
                "human_request_rate": "{:.1%}",
                "efficiency_score": "{:.1%}",
            }
        ),
        use_container_width=True,
    )

with tabs[1]:
    st.dataframe(
        df_tech.sort_values("sessions_total", ascending=False).style.format(
            {
                "sessions_total": "{:,.0f}",
                "retention_rate": "{:.1%}",
                "human_request_rate": "{:.1%}",
                "efficiency_score": "{:.1%}",
            }
        ),
        use_container_width=True,
    )

with tabs[2]:
    st.dataframe(
        df_font.sort_values("sessions_total", ascending=False).style.format(
            {
                "sessions_total": "{:,.0f}",
                "retention_rate": "{:.1%}",
                "human_request_rate": "{:.1%}",
                "efficiency_score": "{:.1%}",
            }
        ),
        use_container_width=True,
    )
