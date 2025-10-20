import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.deterministic import CalendarFourier, DeterministicProcess
from pages.utils.data_loader import get_data
import warnings

warnings.filterwarnings("ignore")

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================
st.set_page_config(page_title="Projeção 2025", page_icon="📈")
st.title("📈 Projeção de Desempenho — até Dezembro de 2025 (SARIMAX + Fourier)")

# ==========================================================
# CARREGAMENTO E PREPARO DOS DADOS
# ==========================================================
df = get_data()
df["date"] = pd.to_datetime(df["date"], errors="coerce")

df_daily = (
    df.groupby("date", as_index=False)
    .agg(
        sessions_total=("sessions_total", "sum"),
        session_retained=("session_retained", "sum"),
    )
    .sort_values("date")
    .reset_index(drop=True)
)
df_daily["retention_rate"] = (
    df_daily["session_retained"] / df_daily["sessions_total"]
).fillna(0)
df_daily["loss_rate"] = 1 - df_daily["retention_rate"]
df_daily = df_daily.set_index("date")


# ==========================================================
# FUNÇÃO DE MODELAGEM — SARIMAX + COMPONENTES FOURIER
# ==========================================================
def forecast_with_fourier(series, steps):
    """
    Ajusta SARIMAX com componentes Fourier para sazonalidade anual (~365 dias)
    e semanal (~7 dias).
    Retorna a média prevista e intervalo de confiança.
    """
    series = series.asfreq("D")

    fourier = CalendarFourier(freq="A", order=6)

    dp = DeterministicProcess(
        index=series.index,
        constant=True,
        order=1,
        seasonal=True,
        additional_terms=[fourier],
        drop=True,
    )

    X = dp.in_sample()
    X_fore = dp.out_of_sample(steps=steps)

    model = SARIMAX(
        series,
        exog=X,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7),
        enforce_stationarity=False,
        enforce_invertibility=False,
    )

    results = model.fit(disp=False)
    forecast = results.get_forecast(steps=steps, exog=X_fore)
    mean_forecast = forecast.predicted_mean
    conf_int = forecast.conf_int()
    return mean_forecast, conf_int


# ==========================================================
# MODELAGEM E PROJEÇÃO
# ==========================================================
last_date = df_daily.index.max()
future_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1), end="2025-12-31", freq="D"
)
n_steps = len(future_dates)

sess_forecast, sess_conf = forecast_with_fourier(df_daily["sessions_total"], n_steps)
ret_forecast, ret_conf = forecast_with_fourier(df_daily["retention_rate"], n_steps)
loss_forecast, loss_conf = forecast_with_fourier(df_daily["loss_rate"], n_steps)

sess_forecast = np.clip(sess_forecast, 0, None)
ret_forecast = np.clip(ret_forecast, 0, 1)
loss_forecast = np.clip(loss_forecast, 0, 1)

df_future = pd.DataFrame(
    {
        "date": future_dates,
        "sessions_total": sess_forecast,
        "retention_rate": ret_forecast,
        "loss_rate": loss_forecast,
        "sess_lower": sess_conf.iloc[:, 0].values,
        "sess_upper": sess_conf.iloc[:, 1].values,
        "ret_lower": ret_conf.iloc[:, 0].values,
        "ret_upper": ret_conf.iloc[:, 1].values,
        "loss_lower": loss_conf.iloc[:, 0].values,
        "loss_upper": loss_conf.iloc[:, 1].values,
    }
).set_index("date")

df_proj = pd.concat([df_daily, df_future])
df_proj["type"] = np.where(df_proj.index <= last_date, "Histórico", "Projeção")

vline_date = last_date

# ==========================================================
# KPIs
# ==========================================================
st.subheader("📊 Indicadores Gerais (SARIMAX + Fourier)")

col1, col2, col3 = st.columns(3)
col1.metric(
    "Último valor de sessões",
    f"{df_daily['sessions_total'].iloc[-1]:,.0f}".replace(",", "."),
)
col2.metric("Retenção atual", f"{df_daily['retention_rate'].iloc[-1]:.1%}")
col3.metric(
    "Retenção projetada (Dez/25)", f"{df_future['retention_rate'].iloc[-1]:.1%}"
)

# ==========================================================
# GRÁFICO 1 — TAXA DE RETENÇÃO
# ==========================================================
st.markdown("### 🔁 Taxa de Retenção — Histórico e Projeção (SARIMAX + Fourier)")

fig_ret = go.Figure()
fig_ret.add_trace(
    go.Scatter(
        x=df_daily.index,
        y=df_daily["retention_rate"],
        mode="lines",
        name="Histórico",
        line=dict(color="#2ca02c"),
    )
)
fig_ret.add_trace(
    go.Scatter(
        x=df_future.index,
        y=df_future["retention_rate"],
        mode="lines",
        name="Projeção",
        line=dict(color="#ff7f0e", dash="dot"),
    )
)
fig_ret.add_trace(
    go.Scatter(
        x=list(df_future.index) + list(df_future.index[::-1]),
        y=list(df_future["ret_upper"]) + list(df_future["ret_lower"][::-1]),
        fill="toself",
        fillcolor="rgba(255,127,14,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=False,
    )
)
fig_ret.add_shape(
    type="line",
    x0=vline_date,
    x1=vline_date,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="gray", dash="dot"),
)
fig_ret.add_annotation(
    x=vline_date,
    y=1,
    xref="x",
    yref="paper",
    text="Início da Projeção",
    showarrow=False,
    yshift=10,
    font=dict(color="gray", size=12),
)
fig_ret.update_layout(
    title="Taxa de Retenção — Histórico e Projeção Diária (SARIMAX + Fourier)",
    yaxis_tickformat=".0%",
    yaxis_title="Taxa de Retenção",
    xaxis_title="Data",
)
st.plotly_chart(fig_ret, use_container_width=True)

# ==========================================================
# GRÁFICO 2 — TAXA DE PERDA
# ==========================================================
st.markdown("### ⚠️ Sessões Não Resolvidas — Histórico e Projeção (SARIMAX + Fourier)")

fig_loss = go.Figure()
fig_loss.add_trace(
    go.Scatter(
        x=df_daily.index,
        y=df_daily["loss_rate"],
        mode="lines",
        name="Histórico",
        line=dict(color="#d62728"),
    )
)
fig_loss.add_trace(
    go.Scatter(
        x=df_future.index,
        y=df_future["loss_rate"],
        mode="lines",
        name="Projeção",
        line=dict(color="#ffa07a", dash="dot"),
    )
)
fig_loss.add_trace(
    go.Scatter(
        x=list(df_future.index) + list(df_future.index[::-1]),
        y=list(df_future["loss_upper"]) + list(df_future["loss_lower"][::-1]),
        fill="toself",
        fillcolor="rgba(255,127,14,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=False,
    )
)
fig_loss.add_shape(
    type="line",
    x0=vline_date,
    x1=vline_date,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="gray", dash="dot"),
)
fig_loss.add_annotation(
    x=vline_date,
    y=1,
    xref="x",
    yref="paper",
    text="Início da Projeção",
    showarrow=False,
    yshift=10,
    font=dict(color="gray", size=12),
)
fig_loss.update_layout(
    title="Taxa de Sessões Não Resolvidas — Histórico e Projeção Diária (SARIMAX + Fourier)",
    yaxis_tickformat=".0%",
    yaxis_title="Taxa de Perda (Loss)",
    xaxis_title="Data",
)
st.plotly_chart(fig_loss, use_container_width=True)

# ==========================================================
# GRÁFICO 3 — VOLUME DE SESSÕES
# ==========================================================
st.markdown("### 📈 Volume Diário — Histórico e Projeção (SARIMAX + Fourier)")

fig_sessions = go.Figure()
fig_sessions.add_trace(
    go.Scatter(
        x=df_daily.index,
        y=df_daily["sessions_total"],
        mode="lines",
        name="Histórico",
        line=dict(color="#1f77b4"),
    )
)
fig_sessions.add_trace(
    go.Scatter(
        x=df_future.index,
        y=df_future["sessions_total"],
        mode="lines",
        name="Projeção",
        line=dict(color="#ff7f0e", dash="dot"),
    )
)
fig_sessions.add_trace(
    go.Scatter(
        x=list(df_future.index) + list(df_future.index[::-1]),
        y=list(df_future["sess_upper"]) + list(df_future["sess_lower"][::-1]),
        fill="toself",
        fillcolor="rgba(255,127,14,0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=False,
    )
)
fig_sessions.add_shape(
    type="line",
    x0=vline_date,
    x1=vline_date,
    y0=0,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="gray", dash="dot"),
)
fig_sessions.add_annotation(
    x=vline_date,
    y=1,
    xref="x",
    yref="paper",
    text="Início da Projeção",
    showarrow=False,
    yshift=10,
    font=dict(color="gray", size=12),
)
fig_sessions.update_layout(
    title="Volume Diário de Sessões — Histórico vs Projeção (SARIMAX + Fourier)",
    yaxis_title="Sessões Totais",
    xaxis_title="Data",
)
st.plotly_chart(fig_sessions, use_container_width=True)

# ==========================================================
# INTERPRETAÇÃO
# ==========================================================
st.markdown("## 🧠 Interpretação Analítica")

start_ret = df_daily["retention_rate"].iloc[-1]
end_ret = df_future["retention_rate"].iloc[-1]
ret_diff = (end_ret - start_ret) * 100

st.markdown(
    f"""
A projeção foi realizada com **SARIMAX(1,1,1)(1,1,1,7)** e **componentes Fourier (ordem=6)**  
para capturar ciclos **anuais e semanais**.  
O modelo ajusta-se ao comportamento de alta observado no fim do ano passado e projeta  
a repetição desse padrão em 2025.

🔹 Retenção atual: **{start_ret:.1%}**  
🔹 Retenção projetada em Dez/25: **{end_ret:.1%}**  
🔹 Variação esperada: **{ret_diff:.1f} p.p.**
"""
)

# ==========================================================
# CONCLUSÃO
# ==========================================================
st.markdown(
    """
## 🧾 Conclusão

O uso combinado de **SARIMAX + Fourier** agora foi aplicado de forma completa às três métricas principais:
**retenção**, **perda (loss)** e **volume de sessões**, permitindo capturar tanto padrões de curto prazo
(semanas) quanto comportamentos sazonais de longo prazo (picos de fim de ano).
O resultado são projeções mais realistas, coerentes e alinhadas com o comportamento histórico do chatbot.
"""
)
