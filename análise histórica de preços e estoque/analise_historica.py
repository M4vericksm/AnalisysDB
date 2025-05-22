import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns

# =============================
# 1. Configuração da conexão com o MySQL
# =============================
conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='35230358',
    database='VarejoBase'
)

# =============================
# 2. Carregar histórico de preços com nome do produto
# =============================
query_preco = """
SELECT 
    hp.id_registro,
    hp.id_produto,
    p.nome_produto,
    hp.data_alteracao,
    hp.preco_antigo,
    hp.preco_novo,
    hp.motivo
FROM historico_preco hp
JOIN produto p ON hp.id_produto = p.id_produto;
"""

df_preco = pd.read_sql(query_preco, conexao)

# Converter data_alteracao para datetime
df_preco['data_alteracao'] = pd.to_datetime(df_preco['data_alteracao'])

# =============================
# 3. Carregar histórico de estoque com nome do produto e da loja
# =============================
query_estoque = """
SELECT 
    he.id_registro,
    he.id_produto,
    he.id_loja,
    l.nome_loja,
    p.nome_produto,
    he.data_registro,
    he.quantidade_anterior,
    he.quantidade_atual,
    he.tipo_movimentacao,
    he.descricao
FROM historico_estoque he
JOIN loja l ON he.id_loja = l.id_loja
JOIN produto p ON he.id_produto = p.id_produto;
"""

df_estoque = pd.read_sql(query_estoque, conexao)

# Converter data_registro para datetime
df_estoque['data_registro'] = pd.to_datetime(df_estoque['data_registro'])

# Fechar conexão
conexao.close()

# =============================
# 4. Visualizar variação de preço de um produto
# =============================
# Exemplo: Produto ID 1
df_preco_filtrado = df_preco[df_preco['id_produto'] == 1]

plt.figure(figsize=(10, 6))
sns.lineplot(data=df_preco_filtrado, x='data_alteracao', y='preco_novo', marker='o')
plt.title(f'Variação de Preço - {df_preco_filtrado.iloc[0]["nome_produto"]}')
plt.xlabel('Data')
plt.ylabel('Preço (R$)')
plt.grid(True)
plt.tight_layout()
plt.show()

# =============================
# 5. Visualizar histórico de estoque de um produto em uma loja
# =============================
# Exemplo: Produto ID 1 na Loja Shopping Center (ID 1)
df_estoque_filtrado = df_estoque[
    (df_estoque['id_produto'] == 1) &
    (df_estoque['id_loja'] == 1)
]

if not df_estoque_filtrado.empty:
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_estoque_filtrado, x='data_registro', y='quantidade_atual', marker='o')
    plt.title(f'Histórico de Estoque - {df_estoque_filtrado.iloc[0]["nome_produto"]} | Loja: {df_estoque_filtrado.iloc[0]["nome_loja"]}')
    plt.xlabel('Data')
    plt.ylabel('Quantidade em Estoque')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("⚠️ Nenhum registro encontrado para o histórico de estoque.")