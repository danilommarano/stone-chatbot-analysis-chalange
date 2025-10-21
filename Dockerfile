# ==============================================================
# Etapa base — imagem mínima com Python e UV
# ==============================================================
FROM python:3.13-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential git && \
    rm -rf /var/lib/apt/lists/*

# Instala o gerenciador de pacotes uv
RUN pip install uv

# ==============================================================
# Configura ambiente e permissões
# ==============================================================
# Define variável de cache do uv dentro do diretório do app
ENV UV_CACHE_DIR=/app/.uvcache
RUN mkdir -p /app/.uvcache

# Cria um usuário não-root e dá a ele acesso total à pasta /app
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# ==============================================================
# Copia o código e instala dependências
# ==============================================================
COPY --chown=appuser:appuser . /app
RUN uv sync --frozen

# ==============================================================
# Configuração do Streamlit
# ==============================================================
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXSRS_PROTECTION=false

# ==============================================================
# Comando de inicialização
# ==============================================================
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]

