import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="seu_host",
    user="seu_usuario",
    password="sua_senha",
    database="seu_banco"
)

query = "SELECT * FROM sua_tabela"

# Usa pandas para ler direto da conexão
df = pd.read_sql(query, conn)

print(df.head())

conn.close()
# Este código conecta a um banco de dados MySQL, executa uma consulta SQL e lê os resultados em um DataFrame do pandas.
# O DataFrame é então impresso, mostrando as primeiras linhas dos dados retornados pela consulta.