

# 📊 AnalisysDB – Sistema de Análise de Dados de Varejo Multimodelo

---

## 🧾 Visão Geral

O **AnalisysDB** é um sistema completo para análise de dados de varejo que integra múltiplos modelos de bancos de dados para armazenar, processar e analisar informações de vendas, estoque, clientes e produtos. Utiliza:

* **Banco de Dados Relacional (Data Warehouse em MySQL)** para armazenar dados estruturados históricos de vendas, estoque, clientes, produtos e fornecedores, modelados em esquema estrela/floco de neve.
* **Banco NoSQL (MongoDB)** para dados não estruturados, como comentários e avaliações de clientes.
* **Banco Objeto (simulado via ObjectDB com JPA/Maven e CSV)** para dados de produtos.

O sistema suporta processos de ETL, análise OLAP multidimensional, técnicas de Data Mining (como clustering e previsão de vendas), e oferece integração via API REST e dashboards interativos para visualização.

---

## 🎯 Objetivos do Projeto

* Aplicar conhecimentos práticos em bancos de dados Objeto-Relacional, Relacional (Data Warehouse) e NoSQL.
* Desenvolver operações analíticas OLAP com múltiplas dimensões.
* Implementar técnicas de Data Mining (ex: KMeans clustering, previsão SARIMAX).
* Criar uma API de integração para consultar dados distribuídos.
* Fornecer dashboards para visualização de KPIs, análises históricas, tendências e previsões.

---


## 🛠️ Tecnologias e Bibliotecas

* **Java + Maven**: JPA com ObjectDB para persistência objeto-relacional, construção da API REST (via FastAPI/Python para integração).
* **Python**:

  * `pandas`, `matplotlib`, `seaborn`: análise e visualização de dados.
  * `scikit-learn`: clustering (KMeans).
  * `statsmodels`: modelos de previsão SARIMAX.
  * `fastapi` + `uvicorn`: desenvolvimento da API REST.
  * `streamlit`: dashboards interativos.
  * Conectores: `mysql-connector-python`, `pymongo` para integração com bancos.
* **Bancos de Dados**: MySQL (relacional DW), MongoDB (NoSQL), ObjectDB simulado via CSV/JPA.

---

## 🗃️ Modelagem do Data Warehouse

* **Dimensões**: `cliente`, `produto`, `categoria`, `loja`, `funcionario`, `fornecedor`, `promocao`.
* **Fatos**: `venda`, `item_venda`, `estoque`, `compra`, `item_compra`, `avaliacao`.
* Procedures para geração de dados históricos, como `gerar_dados_vendas_2022_2023()`.

---

## 🌐 API de Integração (FastAPI)

* Endpoints principais:

  * `GET /produtos` — lista de produtos (MySQL).
  * `GET /precos_historicos` — histórico de preços (MySQL).
  * `GET /comentarios` — comentários de clientes (MongoDB).
  * `GET /produto_objeto` — dados simulados via ObjectDB (JSON).

Arquivos relacionados: `api/`, `conexao.py`, `db_mysql.py`, `dbmongo.py`, `main.py`.

---

## 📊 Dashboards (Streamlit)

* KPIs exibidos: total de vendas, ticket médio, clientes atendidos, produtos vendidos.
* Filtros interativos: ano, categoria, loja.
* Visualizações gráficas com barras e linhas (`st.bar_chart()`, `st.line_chart()`).

---

## 🔍 Operações OLAP

Implementadas em Python (`olap/`):

* **ROLL-UP**: agregação por categoria e ano.
* **DRILL-DOWN**: detalhamento mensal.
* **SLICE**: seleção por ano.
* **DICE**: seleção combinada por categoria e ano.

---

## 📈 Data Mining e Previsão

* **Clustering**: `clustering.py` aplica KMeans para segmentação de clientes por gasto e número de compras.
* **Previsão de vendas**: SARIMAX em `data mining (previsão de vendas)/forecast.py`.

---

## 🚀 Configuração e Execução

1. **Banco de Dados**

   * Inicie MySQL e MongoDB.
   * Execute scripts SQL em `base de dados/` para criar e popular o Data Warehouse.
   * Insira coleções no MongoDB (`comentarios`, `avaliacoes`).

2. **Ambiente Python**

   ```bash
   cd AnalisysDB
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Rodar API**

   ```bash
   uvicorn api.main:app --reload
   ```

4. **Executar Dashboards e Scripts**

   ```bash
   # Operações OLAP
   python olap/rollup_drilldown.py

   # Clustering
   python clustering.py

   # Previsão de vendas
   python "data mining (previsão de vendas)/forecast.py"

   # Dashboard
   streamlit run dashboard.py
   ```

---

## 📦 Estrutura Java (ObjectDB e API)

* Código-fonte Java localizado em `src/main/java` (JPA, API, OLAP).
* Configurações em `src/main/resources` (`persistence.xml`).
* Build e dependências via `pom.xml`.
* Compilação e execução via Maven (`mvn clean install`, `mvn exec:java`).

---

## 📌 Observações Finais

* Mantenha credenciais sensíveis fora do código, usando arquivo `.env`.
* Projeto extensível para integração com novos bancos e APIs externas.
* Possíveis melhorias: autenticação na API, deploy em nuvem, interface web customizada.

---

## 📄 Entregáveis

* Código-fonte completo.
* Relatório Técnico detalhado.
* Conjunto de dados para testes.
* Manual de utilização.
* Apresentação do projeto.

---

## ⚖️ Critérios de Avaliação

* Correção técnica e funcionamento.
* Abrangência dos requisitos.
* Qualidade da integração entre bancos.
* Qualidade e profundidade das análises.
* Clareza e completude da documentação e apresentação.

---
