import pandas as pd
import matplotlib.pyplot as plt

# Carrega os dados OLAP
df = pd.read_csv('olap_resultado.csv')

# Remove linhas que são totais gerais (onde ano ou mês estão nulos)
df = df.dropna(subset=['year', 'month', 'loja', 'filme'])

# Cria uma coluna de tempo contínuo
df['periodo'] = df['year'].astype(
    str) + '-' + df['month'].astype(int).astype(str).str.zfill(2)

# Agrupa por período e loja (poderia ser por filme também)
tabela = df.groupby(['periodo', 'loja'])[
    'total_vendas'].sum().unstack().fillna(0)

# Plotar gráfico de linha por loja ao longo do tempo
tabela.plot(kind='line', marker='o')
plt.title('Total de Vendas por Loja ao Longo do Tempo')
plt.xlabel('Período (Ano-Mês)')
plt.ylabel('Total de Vendas')
plt.grid(True)
plt.legend(title='Loja')
plt.xticks(rotation=45)
plt.tight_layout()

# Salvar imagem
plt.savefig('grafico_olap_vendas_loja.png', dpi=300, bbox_inches='tight')
plt.show()
