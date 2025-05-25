import mysql.connector

def connect_mysql():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="hian291006",
        database="varejabase"
    )

def get_produtos_mysql():
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produto")
    result = cursor.fetchall()
    conn.close()
    return result

def get_precos_historicos():
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM preco_historico")
    result = cursor.fetchall()
    conn.close()
    return result
