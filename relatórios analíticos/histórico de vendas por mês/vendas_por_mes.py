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
# RELATÓRIO: HISTÓRICO DE VENDAS POR MÊS
# ===============================================

query_mes = """
SELECT 
    DATE_FORMAT(v.data_venda, '%Y-%m') AS mes_ano,
    COUNT(v.id_venda) AS total_vendas,
    SUM(v.valor_total) AS valor_total
FROM venda v
GROUP BY mes_ano
ORDER BY mes_ano;
"""

df_mes = executar_consulta(query_mes)
df_mes['valor_total'] = df_mes['valor_total'].apply(formatar_moeda)

print("\nRelatório: Vendas por Mês")
print(df_mes)

# Gráfico
df_mes_plot = df_mes.copy()
df_mes_plot['valor_total_num'] = df_mes_plot['valor_total'].str.replace(r'[R$.\,]', '', regex=True).astype(float)

plt.figure(figsize=(10,6))
sns.lineplot(data=df_mes_plot, x='mes_ano', y='valor_total_num', marker='o')
plt.title('Faturamento Mensal')
plt.xlabel('Mês')
plt.ylabel('Valor Total Vendido (R$)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Fechar conexão
conexao.close()