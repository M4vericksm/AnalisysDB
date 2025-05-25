from pymongo import MongoClient

def connect_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    return client["varejo"]["comentarios"]

def get_comentarios_mongo():
    colecao = connect_mongo()
    comentarios = list(colecao.find({}, {"_id": 0}))  # sem o campo _id
    return comentarios
