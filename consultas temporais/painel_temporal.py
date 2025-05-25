import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from pymongo import MongoClient

# === 1. MySQL: Total de vendas por mês ===
engine = create_engine('mysql+pymysql://root:hian291006@localhost:3306/teste')

query_mysql = """
SELECT 
    YEAR(data_venda) AS ano,
    MONTH(data_venda) AS mes,
    SUM(valor_total) AS total_vendas
FROM vendas
GROUP BY ano, mes
ORDER BY ano, mes;
"""

df_mysql = pd.read_sql(query_mysql, engine)
df_mysql["fonte"] = "MySQL"

# === 2. ObjectDB via CSV ===
df_objectdb = pd.read_csv("resultado_objectdb.csv")  # colunas: ano, mes, total_vendas
df_objectdb["fonte"] = "ObjectDB"

# Unir vendas MySQL e ObjectDB
df_vendas = pd.concat([df_mysql, df_objectdb], ignore_index=True)
df_vendas["mes_ano"] = df_vendas["ano"].astype(str) + "-" + df_vendas["mes"].astype(str).str.zfill(2)

# === 3. MongoDB: Média da nota e volume de avaliações ===
client = MongoClient("mongodb://localhost:27017/")
db = client["ADB"]
collection = db["avaliacoes"]

pipeline = [
    {
        "$group": {
            "_id": {
                "ano": { "$year": "$data_avaliacao" },
                "mes": { "$month": "$data_avaliacao" }
            },
            "media_nota": { "$avg": "$nota" },
            "qtde_avaliacoes": { "$sum": 1 }
        }
    },
    { "$sort": { "_id.ano": 1, "_id.mes": 1 } }
]

resultado_mongo = list(collection.aggregate(pipeline))

df_avaliacoes = pd.DataFrame([{
    "ano": r["_id"]["ano"],
    "mes": r["_id"]["mes"],
    "media_nota": round(r["media_nota"], 2),
    "qtde_avaliacoes": r["qtde_avaliacoes"]
} for r in resultado_mongo])

df_avaliacoes["mes_ano"] = df_avaliacoes["ano"].astype(str) + "-" + df_avaliacoes["mes"].astype(str).str.zfill(2)

# === 4. Painel Comparativo ===
fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Gráfico de vendas
for fonte in df_vendas["fonte"].unique():
    dados = df_vendas[df_vendas["fonte"] == fonte]
    axs[0].plot(dados["mes_ano"], dados["total_vendas"], marker="o", label=f"Vendas - {fonte}")

axs[0].set_title("Evolução das Vendas (MySQL + ObjectDB)")
axs[0].set_ylabel("Total de Vendas")
axs[0].legend()
axs[0].grid(True)

# Gráfico de avaliações
axs[1].bar(df_avaliacoes["mes_ano"], df_avaliacoes["qtde_avaliacoes"], alpha=0.3, label="Qtd Avaliações")
axs[1].plot(df_avaliacoes["mes_ano"], df_avaliacoes["media_nota"], marker="o", color="orange", label="Média das Notas")

axs[1].set_title("Avaliações dos Clientes (MongoDB)")
axs[1].set_xlabel("Mês/Ano")
axs[1].set_ylabel("Notas / Volume")
axs[1].legend()
axs[1].grid(True)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
    