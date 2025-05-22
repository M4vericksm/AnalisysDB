import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# Conexão com MySQL
con = mysql.connector.connect(
    host='localhost',
    user='root',
    password='35230358',
    database='VarejoBase'
)

# Consulta com dimensão loja
query = """
SELECT
    YEAR(v.data_venda) AS ano,
    MONTH(v.data_venda) AS mes,
    l.nome_loja,
    SUM(iv.quantidade * iv.preco_unitario) AS total_vendido
FROM
    venda v
JOIN
    loja l ON v.id_loja = l.id_loja
JOIN
    item_venda iv ON v.id_venda = iv.id_venda
GROUP BY
    ano, mes, l.nome_loja
ORDER BY
    ano, mes, l.nome_loja;
"""

df = pd.read_sql(query, con)
con.close()

# Criar coluna de período
df['periodo'] = df['ano'].astype(str) + '-' + df['mes'].astype(int).astype(str).str.zfill(2)

# Agrupar por loja e período
tabela = df.groupby(['periodo', 'nome_loja'])['total_vendido'].sum().unstack().fillna(0)

# Plotar gráfico com todas as labels no eixo X
plt.figure(figsize=(12, 6))
tabela.plot(kind='line', marker='o')
plt.title('Vendas por Loja ao Longo do Tempo')
plt.xlabel('Período')
plt.ylabel('Total Vendido (R$)')
plt.grid(True)
plt.xticks(ticks=range(len(tabela.index)), labels=tabela.index, rotation=45)
plt.legend(title='Loja', bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.tight_layout()
plt.savefig('grafico_olap_lojas.png', dpi=300)
plt.show()
