# ==============================================================
# Etapa base — imagem mínima com Python e UV
# ==============================================================
FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential git && \
    rm -rf /var/lib/apt/lists/*

# Instala o gerenciador de pacotes uv
RUN pip install uv

# ⚠️ Define variável de ambiente para o cache do uv
ENV UV_CACHE_DIR=/app/.cache/uv

# Cria o diretório do cache com permissão
RUN mkdir -p /app/.cache/uv && chmod -R 777 /app/.cache

# Copia os arquivos do projeto
COPY . .

# Instala dependências via uv
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

