import streamlit as st
import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="hian291006",
    database="varejobase"
)

query = "SELECT * FROM cliente"  # Corrija aqui com o nome correto da tabela
df = pd.read_sql(query, conn)
conn.close()

st.title("Dashboard MySQL com Streamlit")
st.write("Visualização dos dados")
st.dataframe(df)

# Exemplo de gráfico se a coluna 'cliente' for numérica ou quiser contar ocorrências
if 'cliente' in df.columns:
    st.bar_chart(df['cliente'])
