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

# Consulta OLAP
query = """
SELECT
    YEAR(v.data_venda) AS ano,
    MONTH(v.data_venda) AS mes,
    l.nome_loja,
    c.nome_categoria,
    p.descricao AS produto,
    SUM(iv.quantidade * iv.preco_unitario) AS total_vendido
FROM
    venda v
JOIN
    loja l ON v.id_loja = l.id_loja
JOIN
    item_venda iv ON v.id_venda = iv.id_venda
JOIN
    produto p ON iv.id_produto = p.id_produto
JOIN
    categoria c ON p.id_categoria = c.id_categoria
GROUP BY
    ano, mes, l.nome_loja, c.nome_categoria, p.descricao
ORDER BY
    ano, mes, l.nome_loja, c.nome_categoria, p.descricao;
"""

df = pd.read_sql(query, con)
con.close()

# Criar coluna de período
df['periodo'] = df['ano'].astype(str) + '-' + df['mes'].astype(int).astype(str).str.zfill(2)

# Agrupar por categoria e período
tabela = df.groupby(['periodo', 'nome_categoria'])['total_vendido'].sum().unstack().fillna(0)

# Gráfico de linha por categoria
tabela.plot(kind='line', marker='o')
plt.title('Vendas por Categoria ao Longo do Tempo')
plt.xlabel('Período')
plt.ylabel('Total Vendido (R$)')
plt.grid(True)
plt.xticks(rotation=45)
plt.legend(title='Categoria')
plt.tight_layout()
plt.savefig('grafico_olap_categoria.png', dpi=300)
plt.show()
