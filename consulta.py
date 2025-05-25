import streamlit as st
import pandas as pd
import mysql.connector

# ============================
# Conexão com o MySQL
# ============================
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="hian291006",
    database="VarejoBase"
)

# ============================
# Carregar dados das tabelas principais
# ============================
query = """
SELECT v.id_venda, v.data_venda, v.valor_total, v.id_cliente, 
       iv.quantidade, iv.id_produto, p.nome_produto, c.nome_categoria
FROM venda v
JOIN item_venda iv ON v.id_venda = iv.id_venda
JOIN produto p ON p.id_produto = iv.id_produto
JOIN categoria c ON c.id_categoria = p.id_categoria
"""
df = pd.read_sql(query, conn)
conn.close()

# ============================
# Tratamento dos dados
# ============================
df['data_venda'] = pd.to_datetime(df['data_venda'])
df['ano'] = df['data_venda'].dt.year
df['mes'] = df['data_venda'].dt.month_name()

# ============================
# Filtro por ano
# ============================
anos_disponiveis = sorted(df['ano'].unique(), reverse=True)
ano_selecionado = st.sidebar.selectbox("Selecione o ano", anos_disponiveis)
df_filtrado = df[df['ano'] == ano_selecionado]

# ============================
# KPIs
# ============================
total_vendas = df_filtrado['valor_total'].sum()
qtd_vendas = df_filtrado['id_venda'].nunique()
ticket_medio = total_vendas / qtd_vendas if qtd_vendas > 0 else 0
clientes_ativos = df_filtrado['id_cliente'].nunique()
total_produtos = df_filtrado['quantidade'].sum()

# Produto mais vendido
produto_mais_vendido = df_filtrado.groupby('nome_produto')['quantidade'].sum().idxmax()
qtd_produto_mais_vendido = df_filtrado.groupby('nome_produto')['quantidade'].sum().max()

# ============================
# Interface
# ============================
st.title("📊 Dashboard de Vendas - VarejoBase")
st.subheader(f"Ano Selecionado: {ano_selecionado}")

col1, col2, col3 = st.columns(3)
col1.metric("Total de Vendas", f"R$ {total_vendas:,.2f}")
col2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
col3.metric("Clientes Atendidos", clientes_ativos)

col4, col5 = st.columns(2)
col4.metric("Produtos Vendidos", int(total_produtos))
col5.metric("Vendas Realizadas", qtd_vendas)

st.info(f"📌 Produto mais vendido: **{produto_mais_vendido}** ({qtd_produto_mais_vendido} unidades)")

# ============================
# Gráfico de Vendas por Categoria
# ============================
st.subheader("📈 Vendas por Categoria")
vendas_categoria = df_filtrado.groupby('nome_categoria')['valor_total'].sum().sort_values(ascending=False)

st.bar_chart(vendas_categoria)

# ============================
# Mostrar tabela opcional
# ============================
if st.checkbox("Mostrar dados brutos"):
    st.dataframe(df_filtrado)
