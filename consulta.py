import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import locale
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
import numpy as np
from datetime import datetime, timedelta

# Configura localização para formatação de moeda (R$)
locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil')  # Windows

# ============================
# Conexão com o MySQL
# ============================
@st.cache_resource
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="hian291006",
        database="VarejoBase"
    )

conn = get_db_connection()

# ============================
# Carregar dados das vendas
# ============================
@st.cache_data
def load_sales_data():
    query_vendas = """
    SELECT v.id_venda, v.data_venda, v.valor_total, v.id_cliente, 
           iv.quantidade, iv.id_produto, p.nome_produto, p.preco_atual,
           c.nome_categoria, l.nome_loja
    FROM venda v
    JOIN item_venda iv ON v.id_venda = iv.id_venda
    JOIN produto p ON p.id_produto = iv.id_produto
    JOIN categoria c ON c.id_categoria = p.id_categoria
    JOIN loja l ON v.id_loja = l.id_loja
    """
    return pd.read_sql(query_vendas, conn)

df = load_sales_data()

# ============================
# Carregar dados de estoque
# ============================
@st.cache_data
def load_inventory_data():
    query_estoque = """
    SELECT p.id_produto, p.nome_produto, p.preco_atual, 
           e.quantidade_atual, e.quantidade_minima, l.nome_loja
    FROM estoque e
    JOIN produto p ON e.id_produto = p.id_produto
    JOIN loja l ON e.id_loja = l.id_loja
    """
    return pd.read_sql(query_estoque, conn)

df_estoque = load_inventory_data()

# ============================
# Pré-processamento
# ============================
df['data_venda'] = pd.to_datetime(df['data_venda'])
df['ano'] = df['data_venda'].dt.year
df['mes'] = df['data_venda'].dt.month_name()

# Ordena meses corretamente
meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
df['mes'] = pd.Categorical(df['mes'], categories=meses_ordem, ordered=True)

# ============================
# Filtros
# ============================
st.sidebar.header("Filtros")

anos_disponiveis = sorted(df['ano'].unique(), reverse=True)
ano_selecionado = st.sidebar.selectbox("Selecione o ano", anos_disponiveis)
df_filtrado = df[df['ano'] == ano_selecionado]

lojas_disponiveis = df['nome_loja'].unique()
loja_selecionada = st.sidebar.selectbox("Filtrar por loja (opcional)", ["Todas"] + list(lojas_disponiveis))

if loja_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['nome_loja'] == loja_selecionada]
    df_estoque = df_estoque[df_estoque['nome_loja'] == loja_selecionada]

# ============================
# Interface principal
# ============================
st.title("📊 Dashboard de Vendas e Estoque - VarejoBase")
st.subheader(f"Ano Selecionado: {ano_selecionado}")

# ============================
# KPIs
# ============================
total_vendas = df_filtrado['valor_total'].sum()
qtd_vendas = df_filtrado['id_venda'].nunique()
ticket_medio = total_vendas / qtd_vendas if qtd_vendas > 0 else 0
clientes_ativos = df_filtrado['id_cliente'].nunique()
total_produtos = df_filtrado['quantidade'].sum()

produto_mais_vendido = df_filtrado.groupby('nome_produto')['quantidade'].sum().idxmax()
qtd_produto_mais_vendido = df_filtrado.groupby('nome_produto')['quantidade'].sum().max()

col1, col2, col3 = st.columns(3)
col1.metric("Total de Vendas", f"R$ {total_vendas:,.2f}")
col2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("Clientes Atendidos", clientes_ativos)

col4, col5 = st.columns(2)
col4.metric("Produtos Vendidos", int(total_produtos))
col5.metric("Vendas Realizadas", qtd_vendas)

st.info(f"📌 Produto mais vendido: **{produto_mais_vendido}** ({qtd_produto_mais_vendido} unidades)")

# ============================
# Seção OLAP
# ============================
st.header("🔍 Análise OLAP")

tab1, tab2, tab3, tab4 = st.tabs(["Roll-Up", "Drill-Down", "Slice", "Dice"])

with tab1:
    st.subheader("ROLL-UP (Categoria x Ano)")
    
    # Agrupar por categoria e ano
    roll_up = df.groupby(['nome_categoria', 'ano']) \
                 .agg({'valor_total': 'sum'}) \
                 .reset_index()
    
    roll_up.rename(columns={
        'nome_categoria': 'Categoria',
        'ano': 'Ano',
        'valor_total': 'Valor Total'
    }, inplace=True)
    
    # Converter para formato monetário para exibição
    roll_up_display = roll_up.copy()
    roll_up_display['Valor Total'] = roll_up_display['Valor Total'].apply(lambda x: locale.currency(x, grouping=True))
    
    st.dataframe(roll_up_display)
    
    # Gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=roll_up, x='Categoria', y='Valor Total', hue='Ano', ax=ax)
    ax.set_title('Vendas por Categoria e Ano (Roll-Up)')
    ax.set_ylabel('Valor Total Vendido (R$)')
    ax.set_xlabel('Categoria')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    st.subheader("DRILL-DOWN (Categoria x Ano x Mês)")
    
    # Agrupar por categoria, ano e mês
    drill_down = df.groupby(['nome_categoria', 'ano', 'mes']) \
                   .agg({'valor_total': 'sum'}) \
                   .reset_index()
    
    drill_down.rename(columns={
        'nome_categoria': 'Categoria',
        'ano': 'Ano',
        'mes': 'Mês',
        'valor_total': 'Valor Total'
    }, inplace=True)
    
    st.dataframe(drill_down)
    
    # Selecionar categoria para visualização
    categoria_selecionada = st.selectbox("Selecione uma categoria para visualização detalhada:", 
                                        df['nome_categoria'].unique())
    
    # Filtrar dados
    drill_plot = drill_down[drill_down['Categoria'] == categoria_selecionada]
    
    if not drill_plot.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=drill_plot, x='Mês', y='Valor Total', hue='Ano', marker='o', ax=ax)
        ax.set_title(f'Drill-Down: Vendas Mensais da Categoria {categoria_selecionada}')
        ax.set_ylabel('Valor Total (R$)')
        ax.set_xlabel('Mês')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.warning("Nenhum dado disponível para a categoria selecionada.")

with tab3:
    st.subheader(f"SLICE (Somente {ano_selecionado})")
    
    slice_data = df[df['ano'] == ano_selecionado]
    st.dataframe(slice_data[['nome_categoria', 'data_venda', 'valor_total', 'nome_loja']].head(10))

with tab4:
    st.subheader("DICE (Filtro específico)")
    
    col1, col2 = st.columns(2)
    categoria_dice = col1.selectbox("Selecione a categoria:", df['nome_categoria'].unique())
    ano_dice = col2.selectbox("Selecione o ano:", df['ano'].unique())
    
    dice = df[(df['nome_categoria'] == categoria_dice) & (df['ano'] == ano_dice)]
    
    if not dice.empty:
        st.dataframe(dice[['data_venda', 'valor_total', 'nome_produto', 'nome_loja']].head(10))
        
        # Resumo estatístico
        st.subheader("Resumo Estatístico")
        st.write(dice['valor_total'].describe())
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")

# ============================
# Seção Previsão de Vendas
# ============================
st.header("🔮 Previsão de Vendas")

@st.cache_data
def prepare_forecast_data():
    # Criar dados agregados mensais por loja e categoria
    df['mes_ano'] = df['data_venda'].dt.to_period('M').dt.to_timestamp()
    forecast_df = df.groupby(['mes_ano', 'nome_loja', 'nome_categoria'])['valor_total'].sum().reset_index()
    forecast_df.rename(columns={'valor_total': 'valor_vendido'}, inplace=True)
    return forecast_df

forecast_df = prepare_forecast_data()

col1, col2 = st.columns(2)
loja_forecast = col1.selectbox("Selecione a loja para previsão:", forecast_df['nome_loja'].unique())
categoria_forecast = col2.selectbox("Selecione a categoria para previsão:", forecast_df['nome_categoria'].unique())

# Filtrar dados para a loja e categoria selecionadas
df_filtrado_forecast = forecast_df[(forecast_df['nome_loja'] == loja_forecast) & 
                                  (forecast_df['nome_categoria'] == categoria_forecast)].copy()

if len(df_filtrado_forecast) < 12:
    st.warning("Dados insuficientes para realizar a previsão. São necessários pelo menos 12 meses de dados históricos.")
else:
    # Preparar dados para o modelo
    df_filtrado_forecast.set_index('mes_ano', inplace=True)
    df_filtrado_forecast = df_filtrado_forecast.asfreq('MS')
    
    # Dividir em treino e teste (80% treino, 20% teste)
    train_size = int(len(df_filtrado_forecast) * 0.8)
    train, test = df_filtrado_forecast.iloc[:train_size], df_filtrado_forecast.iloc[train_size:]
    
    # Treinar modelo SARIMAX
    try:
        model = SARIMAX(train['valor_vendido'],
                        order=(1,1,1),
                        seasonal_order=(1,1,1,12),
                        enforce_stationarity=False,
                        enforce_invertibility=False)
        
        results = model.fit(disp=False)
        
        # Fazer previsões
        forecast = results.get_forecast(steps=len(test) + 6)  # 6 meses extras para previsão futura
        pred_ci = forecast.conf_int()
        predictions = forecast.predicted_mean
        
        # Plotar resultados
        fig, ax = plt.subplots(figsize=(12,6))
        
        # Plotar dados históricos
        ax.plot(train[-12:].index, train[-12:]['valor_vendido'], label='Treino', color='blue')
        
        # Plotar dados reais de teste (se houver)
        if len(test) > 0:
            ax.plot(test.index, test['valor_vendido'], label='Real', color='green')
        
        # Plotar previsões
        ax.plot(predictions.index, predictions, label='Previsão', color='red')
        ax.fill_between(pred_ci.index,
                       pred_ci.iloc[:, 0],
                       pred_ci.iloc[:, 1], color='k', alpha=.2)
        
        ax.legend()
        ax.set_title(f'Previsão de Vendas - {loja_forecast} | {categoria_forecast}')
        ax.set_ylabel('Valor Vendido (R$)')
        ax.set_xlabel('Mês')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Avaliação do modelo (se houver dados de teste)
        if len(test) > 0:
            test_predictions = predictions[:len(test)]
            rmse = np.sqrt(mean_squared_error(test['valor_vendido'], test_predictions))
            st.info(f"Erro médio quadrático (RMSE) para os dados de teste: R$ {rmse:,.2f}")
        
        # Mostrar previsões futuras
        future_dates = [predictions.index[-1] + timedelta(days=30*i) for i in range(1, 7)]
        future_predictions = predictions[-6:]
        
        st.subheader("Previsão para os próximos 6 meses:")
        future_df = pd.DataFrame({
            'Mês': future_dates,
            'Previsão (R$)': future_predictions.values
        })
        st.dataframe(future_df.style.format({'Previsão (R$)': "{:,.2f}"}))
        
    except Exception as e:
        st.error(f"Erro ao criar o modelo de previsão: {str(e)}")

# ============================
# Gráfico: Vendas por Categoria
# ============================
st.subheader("📈 Vendas por Categoria")
vendas_categoria = df_filtrado.groupby('nome_categoria')['valor_total'].sum().sort_values(ascending=False)
st.bar_chart(vendas_categoria)

# ============================
# Análise de Estoque
# ============================
st.subheader("📦 Estoque Atual por Produto e Loja")

df_estoque['Estoque Baixo'] = df_estoque['quantidade_atual'] < df_estoque['quantidade_minima']
estoque_baixo = df_estoque[df_estoque['Estoque Baixo']]

st.dataframe(df_estoque)

if not estoque_baixo.empty:
    st.warning("⚠️ Produtos com estoque abaixo do mínimo:")
    st.dataframe(estoque_baixo)

# ============================
# Gráfico: Quantidade em Estoque por Loja
# ============================
st.subheader("🏬 Quantidade Total em Estoque por Loja")

estoque_por_loja = df_estoque.groupby('nome_loja')['quantidade_atual'].sum().sort_values(ascending=False)
st.bar_chart(estoque_por_loja)

# ============================
# Valor total em estoque por loja
# ============================
st.subheader("💰 Valor Total em Estoque por Loja")

df_estoque['valor_total'] = df_estoque['quantidade_atual'] * df_estoque['preco_atual']
valor_estoque_loja = df_estoque.groupby('nome_loja')['valor_total'].sum().sort_values(ascending=False)

st.dataframe(valor_estoque_loja.rename("Valor Total (R$)").reset_index())

# ============================
# Preço Atual por Produto
# ============================
st.subheader("🔍 Preço Atual por Produto")

preco_atual = df[['nome_produto', 'preco_atual']].drop_duplicates().sort_values(by='preco_atual', ascending=False)
st.dataframe(preco_atual)

# ============================
# Mineração: Top 5 produtos mais vendidos no ano
# ============================
st.subheader("🏆 Top 5 Produtos Mais Vendidos no Ano")

top5 = df_filtrado.groupby('nome_produto')['quantidade'].sum().sort_values(ascending=False).head(5)
st.bar_chart(top5)

# ============================
# Dados brutos
# ============================
if st.checkbox("📄 Mostrar dados brutos de vendas"):
    st.dataframe(df_filtrado)

# Fechar conexão com o banco de dados
conn.close()
