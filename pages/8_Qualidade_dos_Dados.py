import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pages.utils.data_loader import get_data

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================
st.title("🧩 Qualidade dos Dados")

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
# MÉTRICAS DE QUALIDADE
# ==========================================================
total_rows = len(df_filtered)
missing_topic = df_filtered["topic"].isna().mean()
missing_subject = df_filtered["subject"].isna().mean()
duplicate_rows = df_filtered.duplicated().mean()

numeric_cols = ["sessions_total", "session_retained", "sessions_human_assistance"]
invalid_rows = (
    df_filtered[numeric_cols].lt(0).any(axis=1) | df_filtered["sessions_total"].eq(0)
).mean()


# ==========================================================
# GRÁFICOS GAUGE
# ==========================================================
def gauge_chart(value, title, color="#00cc96"):
    """Cria um gauge chart de 0 a 100%."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=(1 - value) * 100,
            number={"suffix": "%"},
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 70], "color": "#ff6b6b"},
                    {"range": [70, 90], "color": "#f9c74f"},
                    {"range": [90, 100], "color": "#90be6d"},
                ],
            },
        )
    )
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig


st.subheader("📊 Indicadores de Qualidade (%)")

col1, col2 = st.columns(2)
col1.plotly_chart(
    gauge_chart(missing_topic, "Tópicos Preenchidos"), use_container_width=True
)
col2.plotly_chart(
    gauge_chart(missing_subject, "Assuntos Preenchidos"), use_container_width=True
)

col3, col4 = st.columns(2)
col3.plotly_chart(
    gauge_chart(duplicate_rows, "Registros Únicos"), use_container_width=True
)
col4.plotly_chart(
    gauge_chart(invalid_rows, "Valores Válidos (sem negativos ou zero)"),
    use_container_width=True,
)

# ==========================================================
# ALERTAS AUTOMÁTICOS
# ==========================================================
st.subheader("🚨 Diagnóstico Automático")

alerts = []
if missing_topic > 0.1:
    alerts.append(f"- ⚠️ {missing_topic:.1%} dos tópicos estão ausentes.")
if missing_subject > 0.1:
    alerts.append(f"- ⚠️ {missing_subject:.1%} dos assuntos estão ausentes.")
if duplicate_rows > 0.05:
    alerts.append(f"- ⚠️ {duplicate_rows:.1%} dos registros são duplicados.")
if invalid_rows > 0:
    alerts.append(
        f"- ⚠️ {invalid_rows:.1%} dos registros têm valores inválidos (negativos ou zero)."
    )

if not alerts:
    st.success("✅ Nenhum problema relevante de qualidade encontrado!")
else:
    st.error("Problemas encontrados:")
    for a in alerts:
        st.write(a)

# ==========================================================
# RESUMO TABULAR DE QUALIDADE
# ==========================================================
st.subheader("📋 Resumo de Completeness por Coluna")

# calcula % de missing por coluna
missing_summary = (
    df_filtered.isna()
    .mean()
    .reset_index()
    .rename(columns={0: "missing_rate", "index": "column"})
)
missing_summary["completeness"] = 1 - missing_summary["missing_rate"]

st.dataframe(
    missing_summary.sort_values("missing_rate", ascending=False).style.format(
        {"missing_rate": "{:.1%}", "completeness": "{:.1%}"}
    ),
    use_container_width=True,
)

# ==========================================================
# RESUMO GERAL
# ==========================================================
st.subheader("🧮 Resumo Geral de Linhas")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Linhas", f"{total_rows:,}".replace(",", "."))
col2.metric("Duplicatas", f"{duplicate_rows*100:.1f}%")
col3.metric(
    "Campos Vazios (Topic + Subject)", f"{(missing_topic + missing_subject)/2:.1%}"
)
