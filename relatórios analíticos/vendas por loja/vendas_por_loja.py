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
# RELATÓRIO: VENDAS POR LOJA
# ===============================================

query_loja = """
SELECT 
    l.nome_loja,
    COUNT(v.id_venda) AS total_vendas,
    SUM(v.valor_total) AS valor_total
FROM venda v
JOIN loja l ON v.id_loja = l.id_loja
GROUP BY l.id_loja, l.nome_loja
ORDER BY valor_total DESC;
"""

df_loja = executar_consulta(query_loja)
df_loja['valor_total'] = df_loja['valor_total'].apply(formatar_moeda)

print("\nRelatório: Vendas por Loja")
print(df_loja)

# Converter valor_total para numérico para ordenação
df_loja['valor_total_num'] = df_loja['valor_total'].str.replace(r'[R$.\,]', '', regex=True).astype(float)

# Ordenar por valor_total_num
df_loja_sorted = df_loja.sort_values(by='valor_total_num', ascending=False)

# Gráfico
plt.figure(figsize=(10,6))
sns.barplot(data=df_loja_sorted, x='nome_loja', y='valor_total_num')
plt.title('Vendas por Loja')
plt.xlabel('Loja')
plt.ylabel('Valor Total Vendido (R$)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Fechar conexão
conexao.close()