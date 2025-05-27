

# 📊 AnalisysDB – Sistema de Análise de Dados de Varejo Multimodelo

> **Projeto acadêmico e experimental** para integração, processamento e análise de dados de vendas no varejo utilizando múltiplos modelos de bancos de dados. Desenvolvido com foco em ETL, OLAP, Data Mining e visualização interativa.

---

## 🧾 Visão Geral

O **AnalisysDB** é um sistema completo para análise de dados de varejo, que simula um ecossistema multimodelo envolvendo bancos **relacionais**, **NoSQL** e **orientado a objetos**:

* **Relacional (MySQL)** – dados estruturados: vendas, estoque, clientes, etc.
* **NoSQL (MongoDB)** – dados não estruturados: comentários e avaliações de produtos.
* **Objeto (ObjectDB via JPA)** – simulação de persistência orientada a objetos com dados de produtos.

O sistema abrange todas as etapas: ingestão, transformação, análise e visualização. Com ele, é possível explorar tendências históricas, executar consultas temporais, aplicar técnicas de mineração de dados e acessar dashboards em tempo real.

---

## 🎯 Objetivos do Projeto

* Aplicar técnicas de integração e análise com bancos de dados heterogêneos.
* Simular um ecossistema completo de BI (Business Intelligence) para o setor varejista.
* Desenvolver módulos para:

  * ETL e criação de Data Warehouse (DW)
  * OLAP (ROLL-UP, DRILL-DOWN, SLICE, DICE)
  * Mineração de dados (clustering e previsão)
  * API REST para acesso aos dados
  * Dashboard interativo com indicadores de desempenho

---

## 🛠️ Tecnologias Utilizadas

### **Bancos de Dados**

* 📦 MySQL – modelo relacional (esquema estrela/floco de neve)
* 📦 MongoDB – dados semiestruturados (JSON)
* 📦 ObjectDB (via JPA) – persistência orientada a objetos

### **Back-end**

* Java + Maven + JPA – integração com ObjectDB
* Python:

  * `pandas`, `scikit-learn`, `statsmodels`, `matplotlib`, `seaborn`
  * `mysql-connector-python`, `pymongo`
  * `FastAPI`, `Uvicorn` – criação da API REST
  * `Streamlit` – dashboards interativos

---

## 🗂️ Estrutura do Repositório

```
├── análise histórica de preços e estoque/       # Análises de flutuação de preços e estoque
├── api/                                         # API REST com FastAPI
├── base de dados/                               # Scripts SQL para criação do DW
├── consultas temporais/                         # Queries e análises baseadas em data
├── dashboard                                    # Dashboard com KPIs em Streamlit 
├── data mining/                                 # Modelos SARIMAX, pipelines e KMeans
├── mongo.db/                                    # Scripts de ingestão e análise em MongoDB
├── object/                                      # Projeto Java com JPA + ObjectDB
├── olap/                                        # Scripts de OLAP: roll-up, drill-down etc.
├── venv/                                        # Ambiente virtual Python
├── pom.xml                                      # Configuração Maven
├── .gitignore                                   # Arquivos ignorados
└── README.md                                    # Documentação principal
```

---

## 🧱 Modelagem do Data Warehouse

### 🎯 Fato

* `venda`, `item_venda`, `estoque`, `compra`, `item_compra`, `avaliacao`

### 🧩 Dimensões

* `cliente`, `produto`, `categoria`, `loja`, `funcionario`, `fornecedor`, `promocao`

### 🔁 Procedimentos

* `gerar_dados_vendas_2022_2023()` – geração de dados históricos simulados

---

## 🌐 API REST – FastAPI

Integração leve para consulta e visualização dos dados dos diferentes bancos:

| Método | Endpoint             | Fonte de Dados  | Descrição                       |
| ------ | -------------------- | --------------- | ------------------------------- |
| GET    | `/produtos`          | MySQL           | Lista de produtos               |
| GET    | `/precos_historicos` | MySQL           | Histórico de preços por produto |
| GET    | `/comentarios`       | MongoDB         | Comentários e avaliações        |
| GET    | `/produto_objeto`    | JSON (simulado) | Exemplo de acesso via ObjectDB  |

> Local: `api/`, `main.py`, `db_mysql.py`, `dbmongo.py`, `conexao.py`

---

## 📊 Dashboards – Streamlit

Dashboard interativo com indicadores de desempenho e filtros dinâmicos:

* **Indicadores**: total de vendas, ticket médio, número de clientes, produtos vendidos
* **Gráficos**: de barras, de linha, séries temporais
* **Filtros**: ano, loja, categoria

```bash
streamlit run dashboard.py
```

---

## 🔍 OLAP – Análise Multidimensional

Scripts em `olap/` implementam operações OLAP:

* `ROLL-UP`: agregação por categoria, loja ou ano
* `DRILL-DOWN`: detalhamento por mês
* `SLICE`: filtro por dimensão
* `DICE`: filtros compostos (ex: ano + categoria)

---

## 📈 Data Mining

### 🔹 Clustering

* `clustering_clientes.py` – algoritmo KMeans para segmentação de clientes com base em gasto total e frequência de compra

### 🔹 Previsão de Vendas

* `previsao_vendas.py` – modelo SARIMAX para prever vendas futuras com base em séries temporais

---

## ⚙️ Instalação e Execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/M4vericksm/AnalisysDB.git
cd AnalisysDB
```

### 2. Banco de Dados

* Iniciar serviços do MySQL e MongoDB
* Executar os scripts de criação em `base de dados/`
* Inserir documentos no MongoDB (`comentarios`, `avaliacoes`, etc.)

### 3. Ambiente Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Rodar API REST

```bash
uvicorn api.main:app --reload
```

### 5. Rodar Scripts

```bash
# OLAP
python olap/grafico_olap.py

# Clustering
python clustering_clientes.py

# Previsão
python "data mining/previsa_vendas.py"
```

---

## ✅ Entregáveis

* ✅ Código-fonte completo (Python, Java)
* ✅ Relatório técnico e documentação integrada
* ✅ Base de dados simulada e scripts de ETL
* ✅ Interface interativa (API REST + Dashboard)
* ✅ Manual de instalação e execução

---

## 📌 Observações Finais

* 🛡 **Segurança**: configure variáveis sensíveis em arquivos `.env`
* 🔄 **Extensibilidade**: suporte a novos bancos (PostgreSQL, APIs REST, Redis)
* 🚀 **Melhorias Futuras**:

  * Deploy em nuvem (Render, Heroku, AWS)
  * Interface Web com autenticação
  * Logs e monitoramento
  * Automação do ETL com Airflow

---

## 👨‍💻 Autores

**Gabriel Jerônimo**

**Hian VInicius**

**Maverick Martins**

Desenvolvedores em formação, apaixonados por dados, infraestrutura e integração de sistemas.

[GitHub: M4vericksm](https://github.com/M4vericksm)

[GitHub: HIANV](https://github.com/HIANV)

[GitHub: gabrieljvrz](https://github.com/gabrieljvrz)

---

> *Este projeto foi desenvolvido com fins educacionais, para simular um ambiente de análise de dados real e interdisciplinar. Todos os dados utilizados são fictícios.*

---

