import streamlit as st
import pandas as pd
import plotly.express as px
from pages.utils.data_loader import get_data

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================
st.set_page_config(page_title="Análise de Agosto", page_icon="📅")
st.title("📅 Análise de Agosto — Desempenho dos Chatbots Stone e Ton")

df = get_data()
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# ==========================================================
# FILTRAR APENAS AGOSTO/2025
# ==========================================================
df_august = df[(df["date"].dt.month == 8) & (df["date"].dt.year == 2025)]

if df_august.empty:
    st.info("⚠️ Nenhum dado disponível para agosto de 2025.")
    st.stop()

# ==========================================================
# AGREGAR MÉTRICAS PRINCIPAIS
# ==========================================================
agg = pd.DataFrame(
    {
        "sessions_total": [df_august["sessions_total"].sum()],
        "session_retained": [df_august["session_retained"].sum()],
        "sessions_human_assistance": [df_august["sessions_human_assistance"].sum()],
    }
)

agg["retention_rate"] = agg["session_retained"] / agg["sessions_total"]
agg["human_request_rate"] = agg["sessions_human_assistance"] / agg["sessions_total"]
agg["loss_rate"] = 1 - agg["retention_rate"]

total_sessions = int(agg["sessions_total"].iloc[0])
retention_rate = agg["retention_rate"].iloc[0]
human_request_rate = agg["human_request_rate"].iloc[0]
loss_rate = agg["loss_rate"].iloc[0]

# ==========================================================
# KPIs
# ==========================================================
st.markdown(
    f"""
## 🧩 1. Visão Geral
"""
)
col1, col2, col3 = st.columns(3)
col1.metric("Sessões Totais", f"{total_sessions:,}".replace(",", "."))
col2.metric("Taxa de Retenção", f"{retention_rate:.1%}")
col3.metric("Taxa de Pedido Humano", f"{human_request_rate:.1%}")

# ==========================================================
# VISÃO GERAL
# ==========================================================
st.markdown(
    f"""

Durante o mês de **agosto**, o volume total de sessões foi **elevado**, refletindo um uso intenso dos canais automatizados de atendimento.  
A maior parte das interações foi concentrada em **dois bots principais**, com destaque para o bot da **marca Ton**, que apresentou maior volume absoluto de atendimentos.

A **taxa média de retenção** se manteve **estável**, próxima de **{retention_rate:.1%}**, enquanto a **taxa de pedido humano** ficou em torno de **{human_request_rate:.1%}**, indicando que cerca de {int(human_request_rate*100/5)*5}% das interações ainda dependem de atendimento humano.

A curva temporal de sessões mostra variações semanais consistentes, com picos nos dias úteis e queda nos finais de semana, reforçando o padrão de uso comercial.
"""
)

st.info(
    "💡 **Insight:** Apesar da boa taxa de retenção, existe espaço para reduzir o volume de pedidos humanos, especialmente em tópicos recorrentes."
)

st.divider()

# ==========================================================
# EVOLUÇÃO DIÁRIA
# ==========================================================
st.markdown("### 📈 Evolução Diária de Sessões e Retenção")

df_daily = df_august.groupby("date", as_index=False).agg(
    sessions_total=("sessions_total", "sum"),
    session_retained=("session_retained", "sum"),
    sessions_human_assistance=("sessions_human_assistance", "sum"),
)

df_daily["retention_rate"] = df_daily["session_retained"] / df_daily["sessions_total"]
df_daily["human_request_rate"] = (
    df_daily["sessions_human_assistance"] / df_daily["sessions_total"]
)

# --- Gráfico 1: Volume ---
fig_daily_volume = px.line(
    df_daily,
    x="date",
    y=["sessions_total", "session_retained"],
    labels={"value": "Sessões", "variable": "Métrica"},
    color_discrete_map={"sessions_total": "#1f77b4", "session_retained": "#2ca02c"},
    title="Tendência de Volume de Sessões Totais e Retidas",
)
st.plotly_chart(fig_daily_volume, use_container_width=True)

# --- Gráfico 2: Taxas ---
fig_daily_rate = px.line(
    df_daily,
    x="date",
    y=["retention_rate", "human_request_rate"],
    labels={
        "value": "Taxa (%)",
        "variable": "Métrica",
        "retention_rate": "Taxa de Retenção",
        "human_request_rate": "Taxa de Pedido Humano",
    },
    color_discrete_map={"retention_rate": "#2ca02c", "human_request_rate": "#d62728"},
    title="Taxas Diárias — Retenção vs Pedido de Atendimento Humano",
)
fig_daily_rate.update_yaxes(tickformat=".0%")
st.plotly_chart(fig_daily_rate, use_container_width=True)

avg_ret = df_daily["retention_rate"].mean()
avg_human = df_daily["human_request_rate"].mean()
diff = (avg_ret - avg_human) * 100

st.info(
    f"💡 **Insight:** As curvas de **retenção** e **pedido humano** apresentam comportamento inversamente proporcional. "
    f"A **taxa média de retenção** foi de **{avg_ret:.1%}**, enquanto a **taxa média de pedidos humanos** ficou em **{avg_human:.1%}**, "
    f"resultando em uma diferença média de **{diff:.1f} p.p.**. Nos dias de maior volume, há leve queda na retenção, sugerindo aumento na complexidade das consultas."
)

# ==========================================================
# ANÁLISE POR TÓPICOS
# ==========================================================
st.markdown("## 🔍 2. Análise por Tópicos (Topics Analysis)")

df_topics = (
    df_august.groupby("topic", as_index=False)
    .agg(
        sessions_total=("sessions_total", "sum"),
        session_retained=("session_retained", "sum"),
        sessions_human_assistance=("sessions_human_assistance", "sum"),
    )
    .sort_values("sessions_total", ascending=False)
    .head(10)
)

df_topics["retention_rate"] = (
    df_topics["session_retained"] / df_topics["sessions_total"]
)
df_topics["human_request_rate"] = (
    df_topics["sessions_human_assistance"] / df_topics["sessions_total"]
)
df_topics["efficiency"] = df_topics["retention_rate"] - df_topics["human_request_rate"]

min_ret_topic = df_topics.loc[df_topics["retention_rate"].idxmin()]
max_ret_topic = df_topics.loc[df_topics["retention_rate"].idxmax()]

df_topics_sorted = df_topics.sort_values("retention_rate", ascending=False)

fig_topics = px.bar(
    df_topics_sorted,
    x="retention_rate",
    y="topic",
    orientation="h",
    color="retention_rate",
    color_continuous_scale="RdYlGn",
    title="Taxa de Retenção por Tópico — Top 10 de Volume",
    labels={"retention_rate": "Taxa de Retenção", "topic": "Tópico"},
)
fig_topics.update_layout(yaxis_categoryorder="total ascending")
st.plotly_chart(fig_topics, use_container_width=True)

st.info(
    f"💡 **Insight:** A taxa de retenção varia significativamente entre os tópicos. "
    f"O melhor desempenho foi em **{max_ret_topic['topic']}** (**{max_ret_topic['retention_rate']:.1%}**) e o pior em **{min_ret_topic['topic']}** (**{min_ret_topic['retention_rate']:.1%}**). "
    f"Isso indica que alguns fluxos estão bem otimizados, enquanto outros ainda requerem ajustes de linguagem e automação."
)

# ==========================================================
# COMPARATIVOS
# ==========================================================
st.markdown("## 🧠 3. Comparativo entre Bots, Tecnologias e Canais — Agosto")


def aggregate_by(column):
    df_grouped = df_august.groupby(column, as_index=False).agg(
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

col1, col2, col3 = st.columns(3)

with col1:
    fig_bot = px.bar(
        df_bot.sort_values("sessions_total", ascending=True),
        x="sessions_total",
        y="bot",
        orientation="h",
        color="efficiency_score",
        color_continuous_scale="RdYlGn",
        title="Bots — Volume e Eficiência",
    )
    st.plotly_chart(fig_bot, use_container_width=True)

with col2:
    fig_tech = px.bar(
        df_tech.sort_values("sessions_total", ascending=True),
        x="sessions_total",
        y="tech",
        orientation="h",
        color="efficiency_score",
        color_continuous_scale="RdYlGn",
        title="Tecnologias — Volume e Eficiência",
    )
    st.plotly_chart(fig_tech, use_container_width=True)

with col3:
    fig_font = px.bar(
        df_font.sort_values("sessions_total", ascending=True),
        x="sessions_total",
        y="font",
        orientation="h",
        color="efficiency_score",
        color_continuous_scale="RdYlGn",
        title="Canais — Volume e Eficiência",
    )
    st.plotly_chart(fig_font, use_container_width=True)

# Obter registros de melhor e pior desempenho em cada categoria
best_bot = df_bot.loc[df_bot["efficiency_score"].idxmax()]
worst_bot = df_bot.loc[df_bot["efficiency_score"].idxmin()]

best_tech = df_tech.loc[df_tech["efficiency_score"].idxmax()]
worst_tech = df_tech.loc[df_tech["efficiency_score"].idxmin()]

best_font = df_font.loc[df_font["efficiency_score"].idxmax()]
worst_font = df_font.loc[df_font["efficiency_score"].idxmin()]

# Detectar canal com volume muito baixo
least_used_font = df_font.loc[df_font["sessions_total"].idxmin()]

st.info(
    f"""
💡 **Insight — Comparativo entre Bots, Tecnologias e Canais:**  
Os resultados de agosto evidenciam **diferenças expressivas de desempenho** entre os principais componentes do ecossistema de atendimento:

- O **{best_bot['bot']}** apresentou **eficiência notavelmente superior** (**{best_bot['efficiency_score']:.1%}**) em relação ao **{worst_bot['bot']}** (**{worst_bot['efficiency_score']:.1%}**).  
- Entre as tecnologias, a **{best_tech['tech']}** manteve **performance consistente** (**{best_tech['efficiency_score']:.1%}**), enquanto a **{worst_tech['tech']}** ficou **bem abaixo da média**, com apenas **{worst_tech['efficiency_score']:.1%}**.  
- Nos canais, **{best_font['font']}** foi o mais eficiente (**{best_font['efficiency_score']:.1%}**), enquanto **{worst_font['font']}** teve desempenho inferior (**{worst_font['efficiency_score']:.1%}**).  
- Além disso, o canal **{least_used_font['font']}** teve **volume mínimo de utilização**, com apenas **{least_used_font['sessions_total']:,} sessões** no mês, indicando baixa relevância ou desuso operacional.

Essas diferenças indicam **maturidade desigual** entre bots, tecnologias e canais, reforçando a necessidade de **ajustes direcionados** nas áreas com menor eficiência e **maior aproveitamento dos ativos mais performáticos**.
"""
)

# ==========================================================
# FUNIL DE ATENDIMENTO
# ==========================================================
st.markdown("## 🔻 4. Funil de Atendimento (Funnel Analysis)")

funnel = {
    "Sessões Totais": df_august["sessions_total"].sum(),
    "Sessões Retidas": df_august["session_retained"].sum(),
    "Sessões Não Resolvidas": df_august["sessions_total"].sum()
    - df_august["session_retained"].sum(),
}
funnel_df = pd.DataFrame(list(funnel.items()), columns=["Etapa", "Quantidade"])
funnel_df["Percentual"] = funnel_df["Quantidade"] / funnel_df.loc[0, "Quantidade"]

fig_funnel = px.funnel(
    funnel_df,
    y="Etapa",
    x="Quantidade",
    color="Etapa",
    color_discrete_sequence=["#1f77b4", "#2ca02c", "#d62728"],
    title="Funil de Atendimento — Totais → Retidas → Não Resolvidas",
)
st.plotly_chart(fig_funnel, use_container_width=True)

st.info(
    f"💡 **Insight:** Em agosto, **{retention_rate:.1%} das sessões foram resolvidas pelo bot**, enquanto **{loss_rate:.1%}** não tiveram desfecho automatizado, "
    "indicando boa automação, mas ainda com oportunidades de melhoria."
)

# ==========================================================
# RECOMENDAÇÕES
# ==========================================================
# ==========================================================
# RECOMENDAÇÕES E CONCLUSÃO
# ==========================================================
st.markdown(
    """
## 📈 5. Conclusão

- O desempenho geral dos chatbots foi **sólido**, com **alta taxa de retenção** e **consistência nas operações automáticas**.  
- Observa-se, contudo, que **alguns tópicos apresentam taxa de retenção bem abaixo da média**, indicando gargalos de entendimento e oportunidades de otimização nos fluxos de atendimento.  
- O **Bot Stone** se destacou com performance muito superior ao **Bot Ton**, demonstrando maior estabilidade e melhor capacidade de resolver solicitações sem intervenção humana.  
- A **Tech B** superou amplamente a **Tech A**, reforçando a importância de aprimorar modelos e configurações na tecnologia menos eficiente.  
- Em relação aos canais, **Chat C** teve uso mínimo em agosto, indicando baixa adesão ou relevância operacional.  

💬 **Síntese:**  
O mês de agosto consolidou o avanço dos canais automatizados, mas também revelou **discrepâncias relevantes entre bots, tecnologias e canais**.  
Para os próximos ciclos, recomenda-se **aprofundar a análise dos tópicos de menor retenção**, **revisar a performance do Bot Ton e da Tech A**, e **avaliar o papel estratégico do Chat C** — garantindo maior equilíbrio na eficiência geral e melhor experiência para o usuário.
"""
)
