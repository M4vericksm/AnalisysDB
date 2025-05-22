import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import locale

# Configura localização para formatação de moeda (R$)
# locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Linux/Mac
locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil')  # Windows (se necessário)

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
# 4. Funções OLAP - Drill Down, Roll Up, Slice, Dice
# ==============================
# Roll Up: Categoria x Ano
roll_up = df.groupby(['nome_categoria', 'ano']) \
             .agg({'valor_total': 'sum'}) \
             .reset_index()

# Renomear colunas para exibição
roll_up.rename(columns={
    'nome_categoria': 'Categoria',
    'ano': 'Ano',
    'valor_total': 'Valor Total'
}, inplace=True)

# Formatar valor como R$
roll_up['Valor Total'] = roll_up['Valor Total'].apply(lambda x: locale.currency(x, grouping=True))

print("\nRoll Up Formatado:")
print(roll_up.head())

# ==============================
# 5. Visualizações
# ==============================
# Converter de volta para numérico para plotagem
roll_up_plot = roll_up.copy()
roll_up_plot['Valor Total'] = roll_up_plot['Valor Total'].apply(lambda x: float(locale.atof(x.replace('R$', '').strip())))

plt.figure(figsize=(12, 6))
sns.barplot(data=roll_up_plot, x='Categoria', y='Valor Total', hue='Ano')
plt.title('Vendas por Categoria e Ano')
plt.ylabel('Valor Total Vendido (R$)')
plt.xlabel('Categoria')
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend(title='Ano')
plt.show()