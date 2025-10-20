import pandas as pd
import streamlit as st
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[2] / "Case_Data_Analyst_Pl.xlsx"


def load_data():
    df = pd.read_excel(DATA_PATH)

    df = df.rename(
        columns={
            "session_date": "date",
            "chatbot": "bot",
            "fonte": "font",
            "tecnologia_do_chatbot": "tech",
            "topico_da_sessao": "topic",
            "assunto_da_sessao": "subject",
            "sessoes_total": "sessions_total",
            "sessoes_retidas": "session_retained",
            "sessoes_com_pedido_de_atendimento": "sessions_human_assistance",
        }
    )

    categorical_columns = ["bot", "font", "tech"]
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("_", " ").str.title()

    df.bot = df.bot.replace("Bot A", "Bot Ton")
    df.bot = df.bot.replace("Bot B", "Bot Stone")

    df.topic = df.topic.replace("Unknown", None)
    df.subject = df.subject.replace("Unknown", None)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for c in ["sessions_total", "session_retained", "sessions_human_assistance"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["date"])
    return df


def get_data():
    """Retorna o DataFrame do session_state, ou o carrega se ainda não existir."""
    if "df" not in st.session_state:
        from pages.utils.data_loader import load_data

        st.session_state["df"] = load_data()
    return st.session_state["df"]
