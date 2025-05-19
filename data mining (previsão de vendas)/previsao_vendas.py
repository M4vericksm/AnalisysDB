import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np

# Carrega o arquivo CSV
df = pd.read_csv('../AnalisysDB/data mining (previsão de vendas)/vendas_mensais.csv')

# Cria uma coluna contínua de tempo para a regressão (ex: 2022.08)
df['periodo'] = df['year'] + (df['month'] / 12)

# Separa variáveis para regressão
X = df[['periodo']]
y = df['total_vendas']

# Cria e treina o modelo
modelo = LinearRegression()
modelo.fit(X, y)

#Gera previsões para os próximos 3 meses
prox_meses = np.array([df['periodo'].max() + i / 12 for i in range(1, 4)]).reshape(-1, 1)
previsoes = modelo.predict(prox_meses)

# Mostra previsões no terminal
print("\nPrevisões para os próximos 3 meses:")
for i, valor in enumerate(previsoes, start=1):
    print(f"Mês {i}: R$ {valor:.2f}")

# Gera gráfico com dados reais e previsões
plt.plot(df['periodo'], y, label='Vendas Reais', marker='o')
plt.plot(prox_meses, previsoes, label='Previsão', marker='x', linestyle='--', color='red')
plt.xlabel('Ano.Mês')
plt.ylabel('Total de Vendas')
plt.title('Previsão de Vendas')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()