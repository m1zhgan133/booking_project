from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import os
from datetime import datetime
from interaction_with_db import * # мое
# ------------------------------- Вспомогательные функции -------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://myuser:mypassword@localhost:5432/mydatabase"
    # postgresql://<username>:<password>@<host>:<port>/<database_name>
)

# Общая функции для возврата ошибки в формате json
def error_response(message, status_code):
    return jsonify({"error": message}), status_code

def get_connection():
    connection = psycopg2.connect(DATABASE_URL)
    return connection

#------------------------- Запуск DB -------------------------
def wait_for_db():
    conn = psycopg2.connect(
        dbname="mydb",
        user="myuser",
        password="mypassword",
        host="localhost",
        port="5432"
    )
    conn.close()


def initialize_database():
    Base.metadata.create_all(bind=engine)


app = Flask(__name__)

with app.app_context():
    wait_for_db()
    initialize_database()

@app.route('/registration', methods=['POST'])
def create_user_():
    """Создать нового пользователя"""
    data = request.json
    if not data:
        return error_response("no data, try again", 400)
    if not data['name'] or not data['password']:
        return error_response("the name and the password are required", 400)
    if len(data['name']) > 100 or len(data['password']) > 100:
        return error_response("name or password is to long(max length 100 chars)", 400)

    create_user(
        name=data['name'],
        password=data['password']
    )
    return jsonify({"message": "user was successfully created"}), 201


# if __name__ == '__main__':
#     app.run(debug=True)