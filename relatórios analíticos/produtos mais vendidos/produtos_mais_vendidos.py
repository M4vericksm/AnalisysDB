import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import locale

# Configura localização para moeda brasileira
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Linux/Mac
except:
    locale.setlocale(locale.LC_ALL, '')  # Windows

# Conexão com o banco
conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='35230358',
    database='VarejoBase'
)

# Função para formatar como R$
def formatar_moeda(valor):
    return locale.currency(valor, grouping=True)

# Função para rodar consulta e retornar DataFrame
def executar_consulta(query):
    return pd.read_sql(query, conexao)

# ===============================================
# RELATÓRIO: PRODUTOS MAIS VENDIDOS
# ===============================================

query_produtos = """
SELECT 
    p.nome_produto,
    c.nome_categoria,
    SUM(iv.quantidade) AS quantidade_vendida,
    SUM(iv.valor_total) AS valor_total
FROM item_venda iv
JOIN produto p ON iv.id_produto = p.id_produto
JOIN categoria c ON p.id_categoria = c.id_categoria
GROUP BY p.id_produto, p.nome_produto, c.nome_categoria
ORDER BY quantidade_vendida DESC
LIMIT 10;
"""

df_produtos = executar_consulta(query_produtos)
df_produtos['valor_total'] = df_produtos['valor_total'].apply(formatar_moeda)

print("\nRelatório: Produtos Mais Vendidos")
print(df_produtos)

# Gráfico
plt.figure(figsize=(10,6))
sns.barplot(data=df_produtos, x='nome_produto', y='quantidade_vendida')
plt.title('Produtos Mais Vendidos')
plt.xlabel('Produto')
plt.ylabel('Quantidade Vendida')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# Fechar conexão
conexao.close()