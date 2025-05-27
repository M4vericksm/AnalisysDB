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
# RELATÓRIO: VENDAS POR CATEGORIA
# ===============================================

query_categoria = """
SELECT 
    c.nome_categoria,
    SUM(iv.quantidade) AS quantidade_vendida,
    SUM(iv.valor_total) AS valor_total
FROM item_venda iv
JOIN produto p ON iv.id_produto = p.id_produto
JOIN categoria c ON p.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.nome_categoria
ORDER BY valor_total DESC;
"""

df_categoria = executar_consulta(query_categoria)
df_categoria['valor_total'] = df_categoria['valor_total'].apply(formatar_moeda)

print("\nRelatório: Vendas por Categoria")
print(df_categoria)

# Gráfico
plt.figure(figsize=(10,6))
sns.barplot(data=df_categoria, x='nome_categoria', y='quantidade_vendida')
plt.title('Vendas por Categoria')
plt.xlabel('Categoria')
plt.ylabel('Quantidade Vendida')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Fechar conexão
conexao.close()