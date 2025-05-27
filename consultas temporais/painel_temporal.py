import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from pymongo import MongoClient

# === 1. MySQL: Total de vendas por mês ===
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
df_mysql["fonte"] = "MySQL"
df_mysql["mes_ano"] = pd.to_datetime(df_mysql["ano"].astype(str) + "-" + df_mysql["mes"].astype(str).str.zfill(2))

# === 2. ObjectDB via CSV ===
try:
    df_objectdb = pd.read_csv("resultado_objectdb.csv")  # colunas: ano, mes, total_vendas
    df_objectdb["fonte"] = "ObjectDB"
    df_objectdb["mes_ano"] = pd.to_datetime(df_objectdb["ano"].astype(str) + "-" + df_objectdb["mes"].astype(str).str.zfill(2))
except FileNotFoundError:
    df_objectdb = pd.DataFrame(columns=["ano", "mes", "total_vendas", "fonte", "mes_ano"])

# === 3. MongoDB: Média da nota e volume de avaliações ===
client = MongoClient("mongodb://localhost:27017/")
db = client["VarejoBase"]  # nome do seu banco
collection = db["avaliacao"]  # nome correto da coleção

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

# ✅ Aqui está a correção importante
df_avaliacoes["mes_ano"] = pd.to_datetime(df_avaliacoes["ano"].astype(str) + "-" + df_avaliacoes["mes"].astype(str).str.zfill(2))

# === 4. Painel Comparativo ===
fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Gráfico de vendas
for fonte in [df_mysql, df_objectdb]:
    if not fonte.empty:
        axs[0].plot(fonte["mes_ano"], fonte["total_vendas"], marker="o", label=f"Vendas - {fonte['fonte'].iloc[0]}")

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