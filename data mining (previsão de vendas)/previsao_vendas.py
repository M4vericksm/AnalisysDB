import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt

# Carregar o CSV exportado do MySQL
df = pd.read_csv('../AnalisysDB/data mining (previsão de vendas)/vendas_mensais.csv')

# Converter mês/ano para datetime e ordenar
df['mes_ano'] = pd.to_datetime(df['mes_ano'])
df = df.sort_values(by='mes_ano').reset_index(drop=True)

# Exibir dados carregados
print("Dados carregados:")
print(df.head())

# Filtrar por loja e categoria (exemplo: Loja Shopping Center - Eletrônicos)
filtro = (df['nome_loja'] == 'Loja Shopping Center') & (df['nome_categoria'] == 'Eletrônicos')
df_filtrado = df[filtro].copy()

# Definir índice temporal
df_filtrado.set_index('mes_ano', inplace=True)

# Ajustar frequência mensal
df_filtrado = df_filtrado.asfreq('MS')

# Treino e teste (80% treino, 20% teste)
train_size = int(len(df_filtrado) * 0.8)
train, test = df_filtrado.iloc[:train_size], df_filtrado.iloc[train_size:]

# Modelo SARIMAX
model = SARIMAX(train['valor_vendido'],
                order=(1,1,1),
                seasonal_order=(1,1,1,12),  # Sazonalidade anual
                enforce_stationarity=False,
                enforce_invertibility=False)

results = model.fit(disp=False)

# Fazer previsões
forecast = results.get_forecast(steps=len(test))
pred_ci = forecast.conf_int()
predictions = forecast.predicted_mean

# Plotar resultados
plt.figure(figsize=(12,6))
plt.plot(train[-24:].index, train[-24:]['valor_vendido'], label='Treino')
plt.plot(test.index, test['valor_vendido'], label='Real')
plt.plot(predictions.index, predictions, label='Previsão', color='r')
plt.fill_between(pred_ci.index,
                 pred_ci.iloc[:, 0],
                 pred_ci.iloc[:, 1], color='k', alpha=.2)
plt.legend()
plt.title('Previsão de Vendas - Loja Shopping Center | Eletrônicos')
plt.ylabel('Valor Vendido')
plt.show()

# Avaliação do modelo (RMSE)
from sklearn.metrics import mean_squared_error
import numpy as np

rmse = np.sqrt(mean_squared_error(test['valor_vendido'], predictions))
print(f"\nErro médio quadrático (RMSE): {rmse:.2f}")