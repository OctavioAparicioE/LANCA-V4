# app/database.py
import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Passw0rd",
        database="camara_anecoica"
    )
    return connection


