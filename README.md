---
title: Chatbot Dashboard
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 📊 Chatbot Dashboard — Stone & Ton

Aplicação **Streamlit multipage** desenvolvida em **Python**, com ambiente gerenciado via **[uv](https://github.com/astral-sh/uv)** e empacotada em **Docker**.  
O dashboard analisa e projeta o desempenho dos **chatbots das marcas Stone e Ton**, apresentando indicadores de retenção, volume de sessões, eficiência por tecnologia e tópicos mais relevantes.

---

## 🧭 Visão Geral

O projeto foi criado para demonstrar:

- A **estruturação dos dados** da base de sessões e tópicos;
- A **análise descritiva** do mês de agosto/2025;
- A **projeção estatística** de retenção e volume até o final de 2025 (via **SARIMAX + Fourier**).

A aplicação é totalmente **interativa**, com múltiplas páginas acessíveis via **sidebar do Streamlit**.

---

## 🧩 Tecnologias Utilizadas

| Categoria                     | Ferramenta                      |
| ----------------------------- | ------------------------------- |
| Frontend                      | Streamlit                       |
| Modelagem Estatística         | statsmodels (SARIMAX + Fourier) |
| Gerenciamento de Dependências | uv                              |
| Containerização               | Docker                          |
| Visualização                  | Plotly Express / Graph Objects  |
| Linguagem                     | Python 3.13                     |

---

## 🚀 Executando Localmente (sem Docker)

```bash
# 1️⃣ Instale o uv (caso ainda não tenha)
pip install uv

# 2️⃣ Instale as dependências do projeto
uv sync

# 3️⃣ Execute o Streamlit localmente
uv run streamlit run app.py
```

Após iniciar, acesse em:
👉 [http://localhost:8501](http://localhost:8501)

---

## 🐳 Executando via Docker

```bash
# 1️⃣ Clone o repositório
git clone https://github.com/danilommarano/stone-chatbot-analysis-chalange
cd stone-chatbot-analysis-chalange

# 2️⃣ Construa a imagem
docker build -t chatbot-dashboard .

# 3️⃣ Rode o container
docker run -p 7860:7860 chatbot-dashboard
```

A aplicação ficará disponível em:
👉 [http://localhost:7860](http://localhost:7860)

---

## ⚙️ Estrutura do Projeto

```
├── app.py                     # Página inicial
├── pages/                     # Páginas do dashboard multipage
│   ├── 1_Estrutura_Dados.py
│   ├── 2_Analise_de_Agosto.py
│   ├── 3_Projeção_Fim_2025.py
│   └── ...
├── pages/utils/               # Funções auxiliares (ex: get_data)
├── requirements.txt or pyproject.toml
├── Dockerfile
└── README.md
```

---

## 🧠 Modelos de Previsão

A projeção é feita com:

- **SARIMAX(1,1,1)(1,1,1,7)** — captura tendência e sazonalidade semanal.
- **Fourier Terms (ordem=6)** — adiciona sazonalidade anual contínua, refletindo picos de uso (ex: fim de ano).

O resultado é uma previsão **realista e suavizada**, capaz de replicar padrões observados no histórico.

---

## 🧾 Licença

Este projeto é distribuído sob a licença **MIT** — uso livre para fins acadêmicos, profissionais e de demonstração.

---

## 👨‍💻 Autor

**Danilo Marano**
Engenheiro de Dados | Abrisuite \
📧 [danilommarano@gmail.com](mailto:danilommarano@gmail.com) \
🌐 [github.com/danilommarano](https://github.com/danilommarano)
