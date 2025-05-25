import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import locale

# Configura localização para formatação de moeda (R$)
locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil')  # Windows

# ==============================
# 1. Conexão com o MySQL
# ==============================
conexao = mysql.connector.connect(
    host='localhost',
    user='root',
    password='35230358',
    database='VarejoBase'
)

# ==============================
# 2. Carregar dados da tabela fato_vendas
# ==============================
query = """
SELECT * FROM fato_vendas;
"""
df = pd.read_sql(query, conexao)
conexao.close()

# ==============================
# 3. Preparação dos dados
# ==============================
df['data_venda'] = pd.to_datetime(df['data_venda'])
df['ano'] = df['data_venda'].dt.year
df['mes'] = df['data_venda'].dt.month_name()
df['valor_total'] = pd.to_numeric(df['valor_total'], errors='coerce')

# Ordena meses corretamente
meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
df['mes'] = pd.Categorical(df['mes'], categories=meses_ordem, ordered=True)

# ==============================
# 4. OLAP - ROLL-UP: Categoria x Ano
# ==============================
roll_up = df.groupby(['nome_categoria', 'ano']) \
             .agg({'valor_total': 'sum'}) \
             .reset_index()

roll_up.rename(columns={
    'nome_categoria': 'Categoria',
    'ano': 'Ano',
    'valor_total': 'Valor Total'
}, inplace=True)

roll_up['Valor Total'] = roll_up['Valor Total'].apply(lambda x: locale.currency(x, grouping=True))

print("\nROLL-UP (Categoria x Ano):")
print(roll_up.head())

# ==============================
# 5. OLAP - DRILL-DOWN: Categoria x Ano x Mês
# ==============================
drill_down = df.groupby(['nome_categoria', 'ano', 'mes']) \
               .agg({'valor_total': 'sum'}) \
               .reset_index()

drill_down.rename(columns={
    'nome_categoria': 'Categoria',
    'ano': 'Ano',
    'mes': 'Mês',
    'valor_total': 'Valor Total'
}, inplace=True)

print("\nDRILL-DOWN (Categoria x Ano x Mês):")
print(drill_down.head())

# ==============================
# 6. SLICE: Apenas ano de 2024
# ==============================
slice_2024 = df[df['ano'] == 2024]

print("\nSLICE (Somente 2024):")
print(slice_2024[['nome_categoria', 'data_venda', 'valor_total']].head())

# ==============================
# 7. DICE: Eletrônicos no ano de 2023
# ==============================
dice = df[(df['nome_categoria'] == 'Eletrônicos') & (df['ano'] == 2023)]

print("\nDICE (Eletrônicos em 2023):")
print(dice[['data_venda', 'valor_total']].head())

# ==============================
# 8. Visualizações
# ==============================

# ROLL-UP plot
roll_up_plot = roll_up.copy()
roll_up_plot['Valor Total'] = roll_up_plot['Valor Total'].apply(lambda x: float(locale.atof(x.replace('R$', '').strip())))

plt.figure(figsize=(12, 6))
sns.barplot(data=roll_up_plot, x='Categoria', y='Valor Total', hue='Ano')
plt.title('Vendas por Categoria e Ano (Roll-Up)')
plt.ylabel('Valor Total Vendido (R$)')
plt.xlabel('Categoria')
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend(title='Ano')
plt.show()

# DRILL-DOWN plot (Exemplo: categoria 'Eletrônicos')
categoria_exemplo = 'Eletrônicos'
drill_plot = drill_down[drill_down['Categoria'] == categoria_exemplo]

plt.figure(figsize=(12, 6))
sns.lineplot(data=drill_plot, x='Mês', y='Valor Total', hue='Ano', marker='o')
plt.title(f'Drill-Down: Vendas Mensais da Categoria {categoria_exemplo}')
plt.ylabel('Valor Total (R$)')
plt.xlabel('Mês')
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend(title='Ano')
plt.show()
