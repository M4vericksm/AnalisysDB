Sistema de Análise de Dados de Varejo Multimodelo
Descrição do Projeto
Sistema para análise de dados de varejo utilizando múltiplos bancos de dados (ObjectDB, Data Warehouse Relacional, MongoDB) para armazenar, processar e analisar informações de vendas, com foco em análises históricas, tendências e previsões.

Objetivos
Aplicar conhecimentos em bancos de dados (Objeto-Relacional, Relacional DW, NoSQL), ETL, OLAP e Data Mining em um contexto prático de análise de varejo.

Tecnologias e Requisitos
Bancos de Dados: ObjectDB (produtos - JPA/Maven), Data Warehouse (vendas históricas - esquema estrela/floco de neve), MongoDB (dados não estruturados).

Análise: Módulo OLAP (3+ dimensões), 2+ técnicas de Data Mining (ex: Clustering, Previsão), Consultas Temporais.

Integração: API para conectar os bancos.

Interface: Dashboard e relatórios para visualização, interface OLAP.

Estrutura do Projeto
Organizado em src/main/java (código Java, JPA, API, OLAP), src/main/resources (configurações, persistence.xml), src/main/python (scripts Data Mining), src/test, target, pom.xml e .gitignore.

Configuração e Instalação
Clonar repositório.

Instalar Maven, SGBD Relacional e MongoDB.

Configurar conexões no código/arquivos de configuração.

Instalar Python e bibliotecas (pandas, scikit-learn, etc.).

Como Usar
Compilar com mvn clean install.

Executar classes principais Java (mvn exec:java) ou scripts Python (python ...).

Utilizar módulos de persistência (ObjectDB), ETL/DW, MongoDB, OLAP, Data Mining e a API de integração conforme implementado.

Entregáveis
Código-fonte, Relatório Técnico, Conjunto de Dados de Teste, Manual de Utilização, Apresentação.

Critérios de Avaliação
Corretude técnica, completude dos requisitos, qualidade da integração, qualidade das análises, documentação e apresentação.
