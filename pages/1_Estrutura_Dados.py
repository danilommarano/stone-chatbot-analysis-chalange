import streamlit as st
from pathlib import Path

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.title("🗂️ Estrutura de Dados")

st.markdown(
    """
A base fornecida contém métricas agregadas sobre o desempenho dos chatbots, como **sessões totais**, **sessões retidas** e **sessões com pedido de atendimento humano**, segmentadas por **marca**, **chatbot**, **canal**, **tecnologia**, **tópico**, **assunto** e **mês**.

Essas colunas representam contagens de sessões dentro de cada grupo, e não sessões individuais. Isso significa que cada linha da base resume um conjunto de atendimentos com as mesmas características.  

A partir dessa estrutura, o primeiro passo foi desenhar um modelo que permitisse análises consistentes tanto no nível agregado quanto, futuramente, no nível de cada sessão.

A proposta de modelagem é um **modelo dimensional em estrela**, onde uma tabela fato central armazena as métricas de desempenho e se conecta a diversas tabelas dimensão que descrevem os atributos do atendimento (**marca**, **canal**, **tecnologia**, **tema**, **data**, etc.).

---
"""
)

# ==========================================================
# INSERÇÃO DA IMAGEM DO DIAGRAMA
# ==========================================================

st.markdown("## 1.1. Estrutura proposta")

# Caminho para a imagem dentro da pasta src
image_path = Path(
    "src/diagrama_modelo_estrela.png"
)  # ajuste o nome do arquivo conforme o seu
if image_path.exists():
    st.image(
        image_path.as_posix(),
        caption="Modelo Dimensional em Estrela — Chatbot",
        use_container_width=True,
    )
else:
    st.warning(
        f"⚠️ A imagem '{image_path}' não foi encontrada. Verifique se ela está na pasta 'src/'."
    )

st.markdown(
    """

O diagrama acima representa o modelo dimensional em estrela proposto para organizar os dados do chatbot.

No centro está a tabela **fact_sessoes**, que armazena as métricas e indicadores de desempenho referentes a cada sessão de atendimento.  
Ao redor dela estão as **tabelas dimensionais**, que contêm os atributos descritivos usados para segmentar e analisar as sessões sob diferentes perspectivas (**canal**, **marca**, **tecnologia**, **tópico**, **assunto** e **data**).

Cada tabela dimensão se conecta à tabela fato por meio de uma **chave primária (PK)** em sua própria estrutura e uma **chave estrangeira (FK)** correspondente na tabela fato.  
Essas relações são do tipo **1:N (um para muitos)** — uma única entrada na dimensão pode estar associada a várias sessões na tabela fato, mas cada sessão pertence a apenas uma instância da dimensão.

---

### 🧩 Fato principal – `fact_sessoes`

Contém um registro para cada sessão de atendimento realizada pelo chatbot.  
É o centro do modelo e armazena as informações quantitativas e os indicadores utilizados nas análises.  

Inclui também alguns campos que ainda não estão presentes na base fornecida, mas que seriam importantes para ampliar o entendimento sobre a eficiência dos atendimentos, tanto automatizados quanto humanos.

| Coluna | Descrição |
|:--------|:-----------|
| id_sessao | Identificador único da sessão |
| id_marca | Referência para a marca (Stone/Ton) |
| id_canal | Canal de atendimento (chat_a, chat_b, etc.) |
| id_tecnologia | Tecnologia usada no canal (tech_a, tech_b) |
| id_topico | Tema macro do atendimento |
| id_assunto | Assunto específico do atendimento |
| id_data | Data ou mês da sessão |
| pedido_atendimento | Indica se o cliente pediu atendimento humano |
| retida | Indica se a sessão foi resolvida pelo bot |
| duracao_segundos | Duração total da sessão |
| mensagens_totais | Quantidade de mensagens trocadas |
| satisfacao_cliente | Nota de satisfação (quando disponível) |

---

### 📚 Dimensões de referência

Descrevem os atributos qualitativos que caracterizam cada sessão.  
Servem para segmentar e contextualizar as métricas da tabela fato.

| Dimensão | Principais campos |
|:----------|:------------------|
| **dim_marca** | id_marca, nome_marca |
| **dim_canal** | id_canal, nome_canal, tipo_canal |
| **dim_tecnologia** | id_tecnologia, nome_tecnologia, fornecedor |
| **dim_topico** | id_topico, nome_topico |
| **dim_assunto** | id_assunto, nome_assunto, id_topico |
| **dim_data** | id_data, data, mês, ano, semana |

---

## 1.2. Vantagens do modelo em estrela

O modelo dimensional em estrela foi escolhido por equilibrar **simplicidade estrutural**, **eficiência de consulta** e **flexibilidade analítica**.  
A seguir estão os principais benefícios aplicados ao contexto dos chatbots Stone e Ton:

### 🧱 Escalabilidade
Novos elementos podem ser adicionados sem alterar a estrutura central.  
Por exemplo, se futuramente surgir um novo canal de atendimento (ex: chat_c) ou uma nova tecnologia (tech_c), basta inserir novos registros em `dim_canal` ou `dim_tecnologia`.  

A tabela `fact_sessoes` continua inalterada, apenas referenciando esses novos valores por meio de suas chaves estrangeiras (`id_canal`, `id_tecnologia`).

**Exemplo:**  
A inclusão de um novo canal “WhatsApp” em `dim_canal` permite que sessões do WhatsApp sejam registradas automaticamente em `fact_sessoes`, sem necessidade de reformular o modelo.

---

### ⚡ Performance
As consultas e agregações são otimizadas porque as dimensões são pequenas e a tabela fato é indexada por chaves numéricas.  
Isso permite gerar painéis de BI com cálculos rápidos de indicadores como **taxa de retenção** ou **volume de atendimentos**.

Mesmo com milhões de sessões em `fact_sessoes`, uma consulta é rápida e eficiente porque os joins são baseados em IDs inteiros.

---

### 📏 Padronização
A estrutura reduz o risco de divergência entre indicadores, já que todos os cálculos partem da mesma **fonte de verdade — `fact_sessoes`**.  

Assim, a taxa de retenção ou o número total de sessões será sempre o mesmo, independentemente da dimensão usada na análise.

**Exemplo:**  
Tanto um analista que analisa a taxa de retenção por `dim_marca` quanto outro que analisa por `dim_topico` obterão valores consistentes, pois ambos usam a mesma definição de `retida` e `sessoes_total` da tabela fato.

---

### 🔍 Flexibilidade analítica
O modelo facilita cruzar informações de diferentes perspectivas sem retrabalho.  

Como todas as dimensões estão ligadas à mesma tabela fato, é possível analisar o desempenho sob diversos recortes.  

**Exemplo:**  
Comparar a taxa de retenção entre **marcas (`dim_marca`)** e **canais (`dim_canal`)** ou entender quais **tópicos (`dim_topico`)** têm maior volume de pedidos de atendimento humano em cada **tecnologia (`dim_tecnologia`)**.  

Tudo isso pode ser feito apenas alterando os filtros ou joins nas consultas, sem mudar a estrutura.

---

## 1.3. Limitações e cuidados do modelo em estrela

Apesar de suas vantagens, o modelo estrela também apresenta alguns pontos de atenção que precisam ser considerados no contexto do chatbot:

### 🔁 Atualização das dimensões
Como as dimensões são tabelas estáticas, é preciso garantir que estejam sempre atualizadas.  

**Exemplo:**  
Se uma nova tecnologia for implantada e não for cadastrada em `dim_tecnologia`, as sessões relacionadas a ela poderão ser carregadas com chave nula (`id_tecnologia = NULL`), prejudicando as análises.

---

### 🧩 Custo inicial de modelagem
A criação e manutenção das dimensões exigem um esforço de **ETL adicional**, especialmente na normalização de nomes de canais, tópicos e assuntos.  
Isso aumenta o trabalho inicial de desenvolvimento, mas compensa em **confiabilidade** e **performance** a longo prazo.

---

### 🏗️ Necessidade de governança
Com o crescimento das fontes de dados, é essencial manter uma **governança clara das dimensões**.  

**Exemplo:**  
Se “chat_a” e “Chat A” forem cadastrados como dois registros diferentes em `dim_canal`, isso pode causar **distorções nos resultados** e **duplicidade de indicadores**.
"""
)
