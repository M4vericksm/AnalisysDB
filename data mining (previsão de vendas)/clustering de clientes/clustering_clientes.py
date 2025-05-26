import pandas as pd
import mysql.connector
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Conexão com MySQL
con = mysql.connector.connect(
    host='localhost',
    user='root',
    password='35230358',
    database='VarejoBase'
)

# Consulta de clientes
query = """
SELECT
    c.id_cliente,
    COUNT(v.id_venda) AS total_compras,
    SUM(v.valor_total) AS total_gasto,
    AVG(v.valor_total) AS media_por_compra
FROM
    cliente c
LEFT JOIN
    venda v ON c.id_cliente = v.id_cliente
GROUP BY
    c.id_cliente;
"""

df = pd.read_sql(query, con)
con.close()

# Preenche valores nulos com 0 (clientes sem compras)
df = df.fillna(0)

# Seleciona colunas para clustering
X = df[['total_compras', 'total_gasto', 'media_por_compra']]

# Aplica KMeans (3 grupos)
modelo = KMeans(n_clusters=3, random_state=42)
df['cluster'] = modelo.fit_predict(X)

# Mostra os dados com os grupos
print(df)

# (Opcional) Visualização em 2D
plt.figure(figsize=(8,6))
plt.scatter(df['total_compras'], df['total_gasto'], c=df['cluster'], cmap='Set1')
plt.xlabel('Total de Compras')
plt.ylabel('Total Gasto')
plt.title('Clustering de Clientes')
plt.grid(True)
plt.savefig('clustering_clientes.png', dpi=300)
plt.show()
