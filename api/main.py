from fastapi import FastAPI
from db_mysql import get_produtos_mysql, get_precos_historicos
from dbmongo import get_comentarios_mongo

app = FastAPI(title="API de Integração - Varejo Inteligente")

@app.get("/produtos")
def listar_produtos():
    return get_produtos_mysql()

@app.get("/precos_historicos")
def listar_precos():
    return get_precos_historicos()

@app.get("/comentarios")
def listar_comentarios():
    return get_comentarios_mongo()

# Exemplo de endpoint simulando consumo de dados do ObjectDB (via JSON externo, etc.)
@app.get("/produto_objeto")
def produto_objeto():
    return {
        "id": 101,
        "nome": "Notebook Dell",
        "caracteristicas": ["Intel i7", "16GB RAM", "512GB SSD"]
    }
    