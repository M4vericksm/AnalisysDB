from sklearn.cluster import KMeans
import pandas as pd

# Dados simulados de clientes
data = pd.DataFrame({
    'customer_id': [1, 2, 3, 4],
    'total_spent': [500, 1500, 700, 2000],
    'num_purchases': [5, 20, 8, 30]
})

# Aplicar o algoritmo KMeans
model = KMeans(n_clusters=2)
data['cluster'] = model.fit_predict(data[['total_spent', 'num_purchases']])

# Mostrar os resultados
print(data)
