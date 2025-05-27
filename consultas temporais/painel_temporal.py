import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# Conexão com MySQL
engine = create_engine('mysql+pymysql://root:hian291006@localhost:3306/VarejoBase')

# Consulta para vendas (MySQL)
query_vendas = """
SELECT 
    YEAR(data_venda) AS ano,
    MONTH(data_venda) AS mes,
    SUM(valor_total) AS total_vendas
FROM venda
GROUP BY ano, mes
ORDER BY ano, mes;
"""
df_vendas = pd.read_sql(query_vendas, engine)
df_vendas["fonte"] = "MySQL"
df_vendas["mes_ano"] = pd.to_datetime(df_vendas["ano"].astype(str) + "-" + df_vendas["mes"].astype(str).str.zfill(2))

# Consulta para avaliações (MySQL)
query_avaliacoes = """
SELECT 
    YEAR(data_avaliacao) AS ano,
    MONTH(data_avaliacao) AS mes,
    AVG(nota) AS media_nota,
    COUNT(*) AS qtde_avaliacoes
FROM avaliacao
GROUP BY ano, mes
ORDER BY ano, mes;
"""
df_avaliacoes = pd.read_sql(query_avaliacoes, engine)
df_avaliacoes["mes_ano"] = pd.to_datetime(df_avaliacoes["ano"].astype(str) + "-" + df_avaliacoes["mes"].astype(str).str.zfill(2))

# Gráficos
fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Vendas
for fonte in [df_vendas]:
    if not fonte.empty:
        axs[0].plot(fonte["mes_ano"], fonte["total_vendas"], marker="o", label=f"Vendas - {fonte['fonte'].iloc[0]}")
axs[0].set_title("Evolução das Vendas")
axs[0].set_ylabel("Total de Vendas")
axs[0].legend()
axs[0].grid(True)

# Avaliações
axs[1].bar(df_avaliacoes["mes_ano"], df_avaliacoes["qtde_avaliacoes"], alpha=0.7, label="Quantidade de Avaliações")
axs[1].plot(df_avaliacoes["mes_ano"], df_avaliacoes["media_nota"], marker="o", color="orange", label="Média das Notas")
axs[1].set_title("Avaliações dos Clientes")
axs[1].set_xlabel("Mês/Ano")
axs[1].set_ylabel("Notas / Volume")
axs[1].legend()
axs[1].grid(True)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()