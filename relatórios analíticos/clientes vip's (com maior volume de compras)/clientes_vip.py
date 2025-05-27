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
# RELATÓRIO: CLIENTES COM MAIOR VOLUME DE COMPRAS
# ===============================================

query_clientes = """
SELECT 
    cl.nome AS nome_cliente,
    COUNT(v.id_venda) AS total_compras,
    SUM(v.valor_total) AS valor_total
FROM venda v
JOIN cliente cl ON v.id_cliente = cl.id_cliente
GROUP BY cl.id_cliente, cl.nome
ORDER BY valor_total DESC
LIMIT 10;
"""

df_clientes = executar_consulta(query_clientes)
df_clientes['valor_total'] = df_clientes['valor_total'].apply(formatar_moeda)

print("\nRelatório: Clientes com Maiores Compras")
print(df_clientes)

# Converter valor_total para numérico para ordenação
df_clientes['valor_total_num'] = df_clientes['valor_total'].str.replace(r'[R$.\,]', '', regex=True).astype(float)

# Ordenar por valor_total_num
df_clientes_sorted = df_clientes.sort_values(by='valor_total_num', ascending=False)

# Gráfico
plt.figure(figsize=(10,6))
sns.barplot(data=df_clientes_sorted, x='nome_cliente', y='valor_total_num')
plt.title('Clientes VIP - Volume de Compras')
plt.xlabel('Cliente')
plt.ylabel('Valor Total Gasto (R$)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Fechar conexão
conexao.close()