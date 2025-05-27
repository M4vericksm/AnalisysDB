import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns
import locale
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np
from sqlalchemy import create_engine
from pymongo import MongoClient
from sklearn.cluster import KMeans

# ==============================
# Página principal do dashboard
# ==============================
st.set_page_config(page_title="Dashboard de Vendas - VarejoBase", layout="wide")
st.title("📊 Dashboard de Vendas e Estoque - VarejoBase")
st.subheader("Análise Multimodelo de Dados")

# Configura localização para moeda brasileira
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Linux/Mac
except:
    locale.setlocale(locale.LC_ALL, '')  # Windows

# ==============================
# Função de conexão ao banco
# ==============================
@st.cache_resource
def conectar():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='35230358',
        database='varejobase'
    )

conn = conectar()

# ==============================
# Carregar dados das vendas
# ==============================
@st.cache_data
def carregar_vendas():
    query = """
    SELECT 
        v.id_venda,
        DATE(v.data_venda) AS data_venda,
        v.id_cliente,
        v.id_loja,
        v.valor_total,
        iv.quantidade,
        p.nome_produto,
        c.nome_categoria,
        l.nome_loja
    FROM venda v
    JOIN item_venda iv ON v.id_venda = iv.id_venda
    JOIN produto p ON iv.id_produto = p.id_produto
    JOIN categoria c ON p.id_categoria = c.id_categoria
    JOIN loja l ON v.id_loja = l.id_loja;
    """
    return pd.read_sql(query, conn)


df_vendas = carregar_vendas()
df_vendas['data_venda'] = pd.to_datetime(df_vendas['data_venda'])
df_vendas['ano'] = df_vendas['data_venda'].dt.year
df_vendas['mes'] = df_vendas['data_venda'].dt.month_name()
df_vendas['valor_total'] = pd.to_numeric(df_vendas['valor_total'], errors='coerce')

# ==============================
# Carregar histórico de preços e estoque
# ==============================
@st.cache_data
def carregar_historico():
    # Histórico de preços
    query_preco = """
    SELECT 
        hp.id_registro,
        hp.id_produto,
        p.nome_produto,
        hp.data_alteracao,
        hp.preco_antigo,
        hp.preco_novo,
        hp.motivo
    FROM historico_preco hp
    JOIN produto p ON hp.id_produto = p.id_produto;
    """
    df_preco = pd.read_sql(query_preco, conn)
    df_preco['data_alteracao'] = pd.to_datetime(df_preco['data_alteracao'])

    # Histórico de estoque
    query_estoque = """
    SELECT 
        he.id_registro,
        he.id_produto,
        he.id_loja,
        l.nome_loja,
        p.nome_produto,
        he.data_registro,
        he.quantidade_anterior,
        he.quantidade_atual,
        he.tipo_movimentacao,
        he.descricao
    FROM historico_estoque he
    JOIN loja l ON he.id_loja = l.id_loja
    JOIN produto p ON he.id_produto = p.id_produto;
    """
    df_estoque = pd.read_sql(query_estoque, conn)
    df_estoque['data_registro'] = pd.to_datetime(df_estoque['data_registro'])

    return df_preco, df_estoque


df_preco, df_estoque = carregar_historico()

# ==============================
# Carregar dados temporais (MySQL, CSV, MongoDB)
# ==============================
@st.cache_data
def carregar_temporal():
    # MySQL vendas mensais
    engine = create_engine('mysql+pymysql://root:35230358@localhost:3306/varejobase')
    query_mysql = """
    SELECT 
        YEAR(data_venda) AS ano,
        MONTH(data_venda) AS mes,
        SUM(valor_total) AS total_vendas
    FROM venda
    GROUP BY ano, mes
    ORDER BY ano, mes;
    """
    df_mysql = pd.read_sql(query_mysql, engine)
    df_mysql['mes_ano'] = pd.to_datetime(df_mysql['ano'].astype(str) + '-' + df_mysql['mes'].astype(str).str.zfill(2))

    # CSV (ObjectDB)
    try:
        df_obj = pd.read_csv('resultado_objectdb.csv')
        df_obj['mes_ano'] = pd.to_datetime(df_obj['ano'].astype(str) + '-' + df_obj['mes'].astype(str).str.zfill(2))
    except:
        df_obj = pd.DataFrame(columns=['ano','mes','total_vendas','mes_ano'])

    # MongoDB avaliações
    client = MongoClient('mongodb://localhost:27017/')
    db = client['ADB']
    collection = db['avaliacoes']
    pipeline = [
        { '$group': { '_id': { 'ano': { '$year': '$data_avaliacao' }, 'mes': { '$month': '$data_avaliacao' } },
                      'media_nota': { '$avg': '$nota' }, 'qtde_avaliacoes': { '$sum': 1 } } },
        { '$sort': { '_id.ano': 1, '_id.mes': 1 } }
    ]
    resultado = list(collection.aggregate(pipeline))
    client.close()
    df_av = pd.DataFrame([{
        'ano': r['_id']['ano'], 'mes': r['_id']['mes'],
        'media_nota': round(r['media_nota'], 2), 'qtde_avaliacoes': r['qtde_avaliacoes'],
        'mes_ano': pd.to_datetime(str(r['_id']['ano']) + '-' + str(r['_id']['mes']).zfill(2))
    } for r in resultado])

    return df_mysql, df_obj, df_av


df_mysql, df_obj, df_avaliacoes = carregar_temporal()

# ==============================
# Carregar clustering de clientes
# ==============================
@st.cache_data
def carregar_clustering():
    query = """
    SELECT
        c.id_cliente,
        COUNT(v.id_venda) AS total_compras,
        SUM(v.valor_total) AS total_gasto,
        AVG(v.valor_total) AS media_por_compra
    FROM cliente c
    LEFT JOIN venda v ON c.id_cliente = v.id_cliente
    GROUP BY c.id_cliente;
    """
    df = pd.read_sql(query, conn).fillna(0)
    X = df[['total_compras', 'total_gasto', 'media_por_compra']]
    kmeans = KMeans(n_clusters=3, random_state=42).fit(X)
    df['cluster'] = kmeans.labels_
    return df


df_clientes_cluster = carregar_clustering()

# ==============================
# Filtros laterais
# ==============================
st.sidebar.header("Filtrar Dados")
anos_disponiveis = sorted(df_vendas['ano'].unique(), reverse=True)
ano_selecionado = st.sidebar.selectbox("Selecione o ano:", anos_disponiveis)
df_ano = df_vendas[df_vendas['ano'] == ano_selecionado]

lojas_disponiveis = ['Todas'] + list(df_vendas['nome_loja'].unique())
loja_selecionada = st.sidebar.selectbox("Filtrar por loja:", lojas_disponiveis)

if loja_selecionada != 'Todas':
    df_ano = df_ano[df_ano['nome_loja'] == loja_selecionada]

# ==============================
# KPIs principais (inalterado)
# ==============================
total_vendas = df_ano['valor_total'].sum()
qtd_vendas = df_ano['id_venda'].nunique()
ticket_medio = total_vendas / qtd_vendas if qtd_vendas > 0 else 0
clientes_ativos = df_ano['id_cliente'].nunique()
produtos_vendidos = df_ano['quantidade'].sum()
produto_mais_vendido = df_ano.groupby('nome_produto')['quantidade'].sum().idxmax()
qtd_produto_mais_vendido = df_ano.groupby('nome_produto')['quantidade'].sum().max()

col1, col2, col3 = st.columns(3)
col1.metric("Total de Vendas", f"{locale.currency(total_vendas, grouping=True)}")
col2.metric("Ticket Médio", f"{locale.currency(ticket_medio, grouping=True)}")
col3.metric("Clientes Ativos", clientes_ativos)

col4, col5 = st.columns(2)
col4.metric("Produtos Vendidos", int(produtos_vendidos))
col5.metric("Produto Mais Vendido", f"{produto_mais_vendido} ({int(qtd_produto_mais_vendido)} unidades)")

# ==============================
# Tabs do dashboard (incluir novos tabs após o quinto)
# ==============================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "Roll-Up", "Drill-Down", "Slice", "Dice", "Relatórios Analíticos", "Previsão de Vendas",
    "Histórico Preços/Estoque", "Evolução Temporal", "Clustering Clientes"
])
# ==============================
# Roll-Up: Vendas por Categoria e Ano
# ==============================
with tab1:
    st.subheader("ROLL-UP: Vendas por Categoria e Ano")
    roll_up_df = df_vendas.groupby(['nome_categoria', 'ano']) \
                          .agg({'valor_total': 'sum'}) \
                          .reset_index()
    roll_up_df['valor_total'] = roll_up_df['valor_total'].apply(lambda x: locale.currency(x, grouping=True))
    st.dataframe(roll_up_df)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=roll_up_df, x='nome_categoria', y='valor_total', hue='ano')
    ax.set_title('Vendas por Categoria e Ano')
    ax.set_ylabel('Valor Total Vendido')
    ax.set_xlabel('Categoria')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# ==============================
# Drill-Down: Por Mês
# ==============================
with tab2:
    st.subheader("DRILL-DOWN: Vendas Mensais por Categoria")
    drill_down_df = df_vendas.groupby(['nome_categoria', 'ano', 'mes']) \
                            .agg({'valor_total': 'sum'}) \
                            .reset_index()
    drill_down_df['mes'] = pd.Categorical(drill_down_df['mes'], categories=[
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ], ordered=True)
    drill_down_df.sort_values(by=['ano', 'mes'], inplace=True)

    categoria_filtro = st.selectbox("Selecione uma categoria para detalhar:", df_vendas['nome_categoria'].unique())
    filtro_drill = drill_down_df[drill_down_df['nome_categoria'] == categoria_filtro]

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=filtro_drill, x='mes', y='valor_total', hue='ano', marker='o', ax=ax)
    ax.set_title(f'Vendas Mensais - {categoria_filtro}')
    plt.xlabel('Mês')
    plt.ylabel('Valor Total (R$)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)

# ==============================
# Slice: Filtrar por ano
# ==============================
with tab3:
    st.subheader(f"SLICE: Vendas de {ano_selecionado}")
    st.dataframe(df_ano[['data_venda', 'nome_loja', 'nome_categoria', 'valor_total']])

# ==============================
# Dice: Filtrar por múltiplas condições
# ==============================
with tab4:
    st.subheader("DICE: Filtro Personalizado")
    col1_dice, col2_dice = st.columns(2)
    categoria_dice = col1_dice.selectbox("Categoria", df_vendas['nome_categoria'].unique())
    loja_dice = col2_dice.selectbox("Loja", df_vendas['nome_loja'].unique())

    dice_df = df_vendas[
        (df_vendas['nome_categoria'] == categoria_dice) &
        (df_vendas['nome_loja'] == loja_dice)
    ]
    st.dataframe(dice_df.head(10))

#RELATÓRIOS ANALÍTICOS
with tab5:
    st.subheader("📊 Relatórios Analíticos")

    # 1. CLIENTES VIPs - TOP 10 CLIENTES COM MAIOR VALOR GASTO
    st.markdown("### 👥 Clientes VIPs")
    query_clientes = """
    SELECT 
        cl.nome AS nome_cliente,
        COUNT(v.id_venda) AS total_compras,
        SUM(v.valor_total) AS valor_total
    FROM venda v
    JOIN cliente cl ON v.id_cliente = cl.id_cliente
    GROUP BY cl.id_cliente, cl.nome
    ORDER BY valor_total DESC
    LIMIT 10;
    """
    df_clientes = pd.read_sql(query_clientes, conn)
    df_clientes['valor_total'] = df_clientes['valor_total'].apply(lambda x: locale.currency(x, grouping=True))
    st.dataframe(df_clientes.rename(columns={'nome_cliente': 'Cliente', 'total_compras': 'Nº Compras', 'valor_total': 'Valor Gasto'}))

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df_clientes, x='nome_cliente', y='valor_total', ax=ax1)
    ax1.set_title('Clientes VIPs - Valor Total Gasto')
    ax1.set_ylabel('Valor Total (R$)')
    ax1.set_xlabel('Cliente')
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # 2. VENDAS POR CATEGORIA
    st.markdown("---")
    st.markdown("### 📊 Vendas por Categoria")
    query_categoria = """
    SELECT 
        c.nome_categoria,
        SUM(iv.quantidade) AS quantidade_vendida,
        SUM(iv.valor_total) AS valor_total
    FROM item_venda iv
    JOIN produto p ON iv.id_produto = p.id_produto
    JOIN categoria c ON p.id_categoria = c.id_categoria
    GROUP BY c.id_categoria, c.nome_categoria
    ORDER BY valor_total DESC;
    """
    df_categoria = pd.read_sql(query_categoria, conn)
    df_categoria['valor_total'] = df_categoria['valor_total'].apply(lambda x: locale.currency(x, grouping=True))
    st.dataframe(df_categoria.rename(columns={'nome_categoria': 'Categoria', 'quantidade_vendida': 'Qtde Vendida', 'valor_total': 'Valor Total'}))

    fig2, ax2 = plt.subplots()
    sns.barplot(data=df_categoria, x='nome_categoria', y='quantidade_vendida')
    ax2.set_title('Quantidade Vendida por Categoria')
    ax2.set_xlabel('Categoria')
    ax2.set_ylabel('Quantidade')
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # 3. HISTÓRICO DE VENDAS MENSAL
    st.markdown("---")
    st.markdown("### 📅 Histórico de Vendas Mensais")
    query_mes = """
    SELECT 
        DATE_FORMAT(v.data_venda, '%Y-%m') AS mes_ano,
        SUM(v.valor_total) AS valor_total
    FROM venda v
    GROUP BY mes_ano
    ORDER BY mes_ano;
    """
    df_mes = pd.read_sql(query_mes, conn)
    df_mes['mes_ano'] = pd.to_datetime(df_mes['mes_ano'])

    fig3, ax3 = plt.subplots()
    sns.lineplot(data=df_mes, x='mes_ano', y='valor_total', marker='o', ax=ax3)
    ax3.set_title('Faturamento Mensal')
    ax3.set_xlabel('Mês/Ano')
    ax3.set_ylabel('Valor Total Vendido (R$)')
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    # 4. VENDAS POR LOJA
    st.markdown("---")
    st.markdown("### 🏪 Vendas por Loja")
    query_loja = """
    SELECT 
        l.nome_loja,
        COUNT(v.id_venda) AS total_vendas,
        SUM(v.valor_total) AS valor_total
    FROM venda v
    JOIN loja l ON v.id_loja = l.id_loja
    GROUP BY l.id_loja, l.nome_loja
    ORDER BY valor_total DESC;
    """
    df_loja = pd.read_sql(query_loja, conn)
    df_loja['valor_total'] = df_loja['valor_total'].apply(lambda x: locale.currency(x, grouping=True))
    st.dataframe(df_loja.rename(columns={'nome_loja': 'Loja', 'total_vendas': 'Total de Vendas', 'valor_total': 'Valor Total'}))

    fig4, ax4 = plt.subplots()
    sns.barplot(data=df_loja, x='nome_loja', y='valor_total', ax=ax4)
    ax4.set_title('Vendas por Loja')
    ax4.set_xlabel('Loja')
    ax4.set_ylabel('Valor Total Vendido (R$)')
    plt.xticks(rotation=45)
    st.pyplot(fig4)

    # 5. PRODUTOS MAIS VENDIDOS
    st.markdown("---")
    st.markdown("### 🏆 Produtos Mais Vendidos")
    query_produtos = """
    SELECT 
        p.nome_produto,
        c.nome_categoria,
        SUM(iv.quantidade) AS quantidade_vendida,
        SUM(iv.valor_total) AS valor_total
    FROM item_venda iv
    JOIN produto p ON iv.id_produto = p.id_produto
    JOIN categoria c ON p.id_categoria = c.id_categoria
    GROUP BY p.id_produto, p.nome_produto, c.nome_categoria
    ORDER BY quantidade_vendida DESC
    LIMIT 10;
    """
    df_produtos = pd.read_sql(query_produtos, conn)
    df_produtos['valor_total'] = df_produtos['valor_total'].apply(lambda x: locale.currency(x, grouping=True))
    st.dataframe(df_produtos[['nome_produto', 'nome_categoria', 'quantidade_vendida', 'valor_total']].rename(columns={
        'nome_produto': 'Produto',
        'nome_categoria': 'Categoria',
        'quantidade_vendida': 'Quantidade Vendida',
        'valor_total': 'Valor Total'
    }))

    fig5, ax5 = plt.subplots()
    sns.barplot(data=df_produtos, x='nome_produto', y='quantidade_vendida', ax=ax5)
    ax5.set_title('Top 10 Produtos por Quantidade Vendida')
    ax5.set_xlabel('Produto')
    ax5.set_ylabel('Quantidade Vendida')
    plt.xticks(rotation=90)
    st.pyplot(fig5)

# ==============================
# Previsão de Vendas com SARIMAX
# ==============================
with tab6:
    st.subheader("🔮 Previsão de Vendas Futuras")

    try:
        # Agrupar vendas mensais por loja e categoria
        forecast_query = """
        SELECT 
            DATE_FORMAT(v.data_venda, '%Y-%m') AS mes_ano,
            l.nome_loja,
            c.nome_categoria,
            SUM(v.valor_total) AS valor_total
        FROM venda v
        JOIN loja l ON v.id_loja = l.id_loja
        JOIN item_venda iv ON v.id_venda = iv.id_venda
        JOIN produto p ON iv.id_produto = p.id_produto
        JOIN categoria c ON p.id_categoria = c.id_categoria
        GROUP BY mes_ano, l.nome_loja, c.id_categoria
        ORDER BY mes_ano;
        """
        forecast_df = pd.read_sql(forecast_query, conn)
        forecast_df['mes_ano'] = pd.to_datetime(forecast_df['mes_ano'])
        forecast_df.set_index('mes_ano', inplace=True)

        # Filtros interativos
        col1, col2 = st.columns(2)
        loja_forecast = col1.selectbox("Selecione a loja para previsão:", forecast_df['nome_loja'].unique())
        categoria_forecast = col2.selectbox("Selecione a categoria:", forecast_df['nome_categoria'].unique())

        # Filtrar dados
        df_forecast = forecast_df[(forecast_df['nome_loja'] == loja_forecast) & (forecast_df['nome_categoria'] == categoria_forecast)].copy()
        df_forecast = df_forecast.resample('MS').sum(numeric_only=True).fillna(0)

        if len(df_forecast) < 12:
            st.warning("⚠️ Dados insuficientes para previsão. São necessários pelo menos 12 meses de dados.")
        else:
            model = SARIMAX(df_forecast['valor_total'], order=(1,1,1), seasonal_order=(1,1,1,12))
            results = model.fit(disp=False)

            steps = 12
            forecast = results.get_forecast(steps=steps)
            pred_ci = forecast.conf_int()
            predictions = forecast.predicted_mean

            pred_df = pd.DataFrame({
                'Data': pd.date_range(df_forecast.index[-1], periods=steps + 1, freq='MS')[1:],
                'Previsão': predictions.values
            }).set_index('Data')

            st.write(f"Previsão de vendas futuras para {loja_forecast} - {categoria_forecast}")
            fig5, ax5 = plt.subplots()
            ax5.plot(df_forecast.index, df_forecast['valor_total'], label='Histórico')
            ax5.plot(pred_df.index, pred_df['Previsão'], label='Previsão', color='r')
            ax5.legend()
            ax5.set_title('Previsão de Vendas com SARIMAX')
            ax5.set_xlabel('Data')
            ax5.set_ylabel('Valor Total (R$)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig5)

            # RMSE
            from sklearn.metrics import mean_squared_error
            rmse = np.sqrt(mean_squared_error(
                df_forecast.tail(6)['valor_total'],
                predictions[:6]
            ))
            st.info(f"Erro médio quadrático (RMSE): R$ {rmse:.2f}")
    except Exception as e:
        st.error(f"🚨 Erro na previsão de vendas: {e}")

# (1) Tab Histórico de Preços e Estoque
with tab7:
    st.subheader("Histórico de Preços")
    prod_p = st.selectbox("Selecione Produto (Preço):", df_preco['nome_produto'].unique())
    df_pp = df_preco[df_preco['nome_produto'] == prod_p]
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df_pp, x='data_alteracao', y='preco_novo', marker='o', ax=ax)
    ax.set_title(f'Variação de Preço - {prod_p}')
    ax.set_xlabel('Data')
    ax.set_ylabel('Preço (R$)')
    st.pyplot(fig)

    st.subheader("Histórico de Estoque")
    prod_e = st.selectbox("Selecione Produto (Estoque):", df_estoque['nome_produto'].unique())
    loja_e = st.selectbox("Selecione Loja (Estoque):", df_estoque['nome_loja'].unique())
    df_ee = df_estoque[(df_estoque['nome_produto'] == prod_e) & (df_estoque['nome_loja'] == loja_e)]
    if not df_ee.empty:
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=df_ee, x='data_registro', y='quantidade_atual', marker='o', ax=ax2)
        ax2.set_title(f'Estoque ao Longo do Tempo - {prod_e} | {loja_e}')
        ax2.set_xlabel('Data')
        ax2.set_ylabel('Quantidade')
        st.pyplot(fig2)
    else:
        st.warning("⚠️ Nenhum registro de estoque para a combinação selecionada.")

# (2) Tab Evolução Temporal
with tab8:
    st.subheader("Evolução Temporal de Métricas")
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    ax3.plot(df_mysql['mes_ano'], df_mysql['total_vendas'], marker='o', label='Vendas MySQL')
    if not df_obj.empty:
        ax3.plot(df_obj['mes_ano'], df_obj['total_vendas'], marker='o', label='Vendas ObjectDB')
    ax3.set_title('Total de Vendas Mensal')
    ax3.set_xlabel('Mês/Ano')
    ax3.set_ylabel('Total Vendas')
    ax3.legend()
    st.pyplot(fig3)

    fig4, ax4 = plt.subplots(figsize=(12, 6))
    ax4.bar(df_av['mes_ano'], df_av['qtde_avaliacoes'], alpha=0.3, label='Qtd Avaliações')
    ax4.plot(df_av['mes_ano'], df_av['media_nota'], marker='o', label='Média Nota')
    ax4.set_title('Avaliações dos Clientes')
    ax4.set_xlabel('Mês/Ano')
    ax4.set_ylabel('Notas / Volume')
    ax4.legend()
    st.pyplot(fig4)

# (1) Tab Histórico de Preços e Estoque
with tab7:
    st.subheader("Histórico de Preços")
    prod_p = st.selectbox("Selecione Produto (Preço):", df_preco['nome_produto'].unique())
    df_pp = df_preco[df_preco['nome_produto'] == prod_p]
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df_pp, x='data_alteracao', y='preco_novo', marker='o', ax=ax)
    ax.set_title(f'Variação de Preço - {prod_p}')
    ax.set_xlabel('Data')
    ax.set_ylabel('Preço (R$)')
    st.pyplot(fig)

    st.subheader("Histórico de Estoque")
    prod_e = st.selectbox("Selecione Produto (Estoque):", df_estoque['nome_produto'].unique())
    loja_e = st.selectbox("Selecione Loja (Estoque):", df_estoque['nome_loja'].unique())
    df_ee = df_estoque[(df_estoque['nome_produto'] == prod_e) & (df_estoque['nome_loja'] == loja_e)]
    if not df_ee.empty:
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=df_ee, x='data_registro', y='quantidade_atual', marker='o', ax=ax2)
        ax2.set_title(f'Estoque ao Longo do Tempo - {prod_e} | {loja_e}')
        ax2.set_xlabel('Data')
        ax2.set_ylabel('Quantidade')
        st.pyplot(fig2)
    else:
        st.warning("⚠️ Nenhum registro de estoque para a combinação selecionada.")

# (2) Tab Evolução Temporal
with tab8:
    st.subheader("Evolução Temporal de Métricas")
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    ax3.plot(df_mysql['mes_ano'], df_mysql['total_vendas'], marker='o', label='Vendas MySQL')
    if not df_obj.empty:
        ax3.plot(df_obj['mes_ano'], df_obj['total_vendas'], marker='o', label='Vendas ObjectDB')
    ax3.set_title('Total de Vendas Mensal')
    ax3.set_xlabel('Mês/Ano')
    ax3.set_ylabel('Total Vendas')
    ax3.legend()
    st.pyplot(fig3)

    fig4, ax4 = plt.subplots(figsize=(12, 6))
    ax4.bar(df_avaliacoes['mes_ano'], df_avaliacoes['qtde_avaliacoes'], alpha=0.3, label='Qtd Avaliações')
    ax4.plot(df_avaliacoes['mes_ano'], df_avaliacoes['media_nota'], marker='o', label='Média Nota')
    ax4.set_title('Avaliações dos Clientes')
    ax4.set_xlabel('Mês/Ano')
    ax4.set_ylabel('Notas / Volume')
    ax4.legend()
    st.pyplot(fig4)

# (3) Tab Clustering de Clientes
with tab9:
    st.subheader("Clustering de Clientes")
    # st.image("grafico_clustering.png", use_column_width=True)
    st.dataframe(df_clientes_cluster)
    fig5, ax5 = plt.subplots(figsize=(8, 6))
    ax5.scatter(
        df_clientes_cluster['total_compras'],
        df_clientes_cluster['total_gasto'],
        c=df_clientes_cluster['cluster'], cmap='Set1'
    )
    ax5.set_xlabel('Total de Compras')
    ax5.set_ylabel('Total Gasto')
    ax5.set_title('Segmentação de Clientes')
    st.pyplot(fig5)

# ==============================
# Mostrar dados brutos
# ==============================
if st.checkbox("📄 Mostrar dados brutos"):
    st.subheader("Dados de Vendas")
    st.dataframe(df_vendas.head(20))

# ==============================
# Fechar conexão
# ==============================
conn.close()
