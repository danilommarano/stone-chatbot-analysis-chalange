import streamlit as st

# ==========================================================
# CONFIGURAÇÃO GERAL
# ==========================================================
st.set_page_config(
    page_title="Início",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# CABEÇALHO
# ==========================================================
st.title("🤖 Chatbot Dashboard — Stone & Ton")

st.markdown(
    """
### 🧭 Visão Geral

Este painel foi desenvolvido para **analisar o desempenho dos chatbots das marcas Stone e Ton**, integrando análises de dados, projeções estatísticas, temas de conversas e qualidade dos atendimentos.

O objetivo é fornecer **insights estratégicos e operacionais** sobre as interações automatizadas, avaliando volume, eficiência, retenção, tópicos mais recorrentes e padrões de atendimento.
"""
)

st.divider()

# ==========================================================
# ÍNDICE DE PÁGINAS
# ==========================================================
st.markdown("## 📚 Índice de Páginas")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/1_Estrutura_Dados.py", label="🧱 Estrutura de Dados", icon="🧩")
    st.markdown(
        "Exibe a **estrutura das bases utilizadas**, com tabelas, colunas e relacionamentos principais dos dados brutos e transformados."
    )

    st.page_link(
        "pages/2_Analise_de_Agosto.py", label="📅 Análise de Agosto", icon="📊"
    )
    st.markdown(
        "Analisa o comportamento do chatbot em **agosto**, destacando sessões, retenção e solicitações de atendimento humano."
    )

    st.page_link(
        "pages/3_Projeção_Fim_2025.py", label="📈 Projeção até o Fim de 2025", icon="📆"
    )
    st.markdown(
        "Modelo **SARIMAX + Fourier** que realiza uma **projeção diária contínua** até dezembro de 2025, "
        "capturando tendências e sazonalidades anuais observadas no histórico."
    )

    st.page_link("pages/4_Visão_Geral.py", label="🌐 Visão Geral", icon="🧭")
    st.markdown(
        "Painel consolidado com os principais indicadores: sessões, retenção, taxa de resolução e volume por canal."
    )

with col2:
    st.page_link("pages/5_Tópicos.py", label="💬 Tópicos", icon="💡")
    st.markdown(
        "Identifica os **principais tópicos e intenções** das conversas, medindo frequência e desempenho por categoria."
    )

    st.page_link("pages/6_Assuntos.py", label="🧠 Assuntos", icon="🧩")
    st.markdown(
        "Agrupa os tópicos em **assuntos macro** e mostra a performance do chatbot em cada grupo temático."
    )

    st.page_link(
        "pages/7_Comparação_de_Tecnologias.py",
        label="⚙️ Comparação de Tecnologias",
        icon="🔬",
    )
    st.markdown(
        "Compara o desempenho entre **diferentes tecnologias de chatbot**, analisando tempos médios, retenção e satisfação."
    )

    st.page_link(
        "pages/8_Qualidade_dos_Dados.py", label="📋 Qualidade dos Dados", icon="🧹"
    )
    st.markdown(
        "Avalia a **consistência e completude** das informações, verificando duplicidades, lacunas e possíveis anomalias."
    )

    st.page_link("pages/9_Análise_de_Funil.py", label="🪄 Análise de Funil", icon="🔻")
    st.markdown(
        "Visualiza o **funil de atendimento**, acompanhando o caminho do usuário desde o início da sessão até a resolução."
    )

st.divider()

# ==========================================================
# COMO NAVEGAR
# ==========================================================
st.markdown(
    """
### 🧾 Como Navegar

- Use o **menu lateral** ou os **links acima** para acessar cada página.  
- Todas as seções são **interativas** e atualizadas dinamicamente.  
- As projeções utilizam modelos estatísticos ajustados automaticamente com base no histórico mais recente.

---

💡 *Desenvolvido por **Danilo Marano*** — Equipe de Dados (Stone & Ton)  
📅 Atualizado automaticamente conforme novas sessões são registradas.
"""
)

st.divider()

# ==========================================================
# SEÇÃO GITHUB
# ==========================================================
st.markdown(
    """
## 📂 Código Fonte no GitHub

O repositório completo do projeto está disponível publicamente no GitHub:  
🔗 [**danilommarano/stone-chatbot-analysis-chalange**](https://github.com/danilommarano/stone-chatbot-analysis-chalange)

Nele, você encontrará:
- O **código completo** do dashboard em Streamlit (organizado por páginas);
- Os **modelos estatísticos** utilizados nas projeções (SARIMAX + Fourier);
- Scripts auxiliares de **pré-processamento e estruturação de dados**;
- Instruções para **execução local via Docker** e **gerenciamento de dependências com `uv`**.

Este repositório foi publicado para garantir **transparência técnica** e facilitar a **reprodutibilidade da análise**.
"""
)
