import plotly.express as px


def daily_sessions_chart(df, enable_smoothing=False):
    if enable_smoothing:
        cols = ["sessions_total", "session_retained", "sessions_human_assistance"]
        df[cols] = df[cols].rolling(7, min_periods=1).mean()

    fig = px.line(
        df,
        x="date",
        y=["sessions_total", "session_retained", "sessions_human_assistance"],
        labels={"value": "Sessões", "variable": "Tipo"},
        title="Evolução diária das sessões"
        + (" (média móvel 7d)" if enable_smoothing else ""),
        markers=True,
    )
    fig.update_layout(template="plotly_white")
    return fig


def retention_rate_chart(df, enable_smoothing=False):
    if enable_smoothing:
        df[["retention_rate", "human_request_rate"]] = (
            df[["retention_rate", "human_request_rate"]]
            .rolling(7, min_periods=1)
            .mean()
        )

    df_plot = df.melt(
        id_vars="date",
        value_vars=["retention_rate", "human_request_rate"],
        var_name="Indicador",
        value_name="Taxa",
    )

    fig = px.line(
        df_plot,
        x="date",
        y="Taxa",
        color="Indicador",
        title="Taxas de retenção e pedido humano"
        + (" (média móvel 7d)" if enable_smoothing else ""),
        markers=True,
    )
    fig.update_layout(yaxis_tickformat=".0%", template="plotly_white")
    return fig
