import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# Carrega os dados
df = pd.read_csv('../AnalisysDB/data mining (previsão de vendas)/vendas_mensais.csv')

# Trata os dados
df['periodo'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)
df['indice_tempo'] = range(len(df))

# Modelo de regressão
X = df[['indice_tempo']]
y = df['total_vendas']
modelo = LinearRegression()
modelo.fit(X, y)

# Previsões para os próximos 3 meses
proximos = pd.DataFrame({'indice_tempo': [len(df), len(df)+1, len(df)+2]})
proximos['previsao'] = modelo.predict(proximos[['indice_tempo']])
proximos['periodo'] = ['Mês+' + str(i+1) for i in range(3)]

# Gráfico
plt.figure(figsize=(10, 5))
plt.plot(df['periodo'], y, marker='o', label='Vendas Reais')
plt.plot(proximos['periodo'], proximos['previsao'], marker='x', linestyle='--', color='red', label='Previsão')
plt.title('Previsão de Vendas Mensais')
plt.xlabel('Período')
plt.ylabel('Total de Vendas')
plt.grid(True)
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig('grafico_previsao_vendas.png', dpi=300)
plt.show()
