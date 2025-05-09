from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import os
from datetime import datetime
import re
import requests
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

def is_datetime(date_str: str) -> bool:
    try:
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$'
        if not bool(re.fullmatch(pattern, date_str)):
            return False
        datetime.fromisoformat(date_str)
    except:
        return False
    return True

def str_time_to_minutes(time_str: str) -> int:
    try:
        hours, minutes = map(int, time_str.split(':'))
        if 0 <= hours < 24 and 0 <= minutes < 60:
            return hours * 60 + minutes
        return -1
    except:
        return -1

def add_minutes_to_datetime(start_datetime_str: str, minutes: int|str) -> str:
        try:
            minutes = int(minutes)
            start_datetime = datetime.fromisoformat(start_datetime_str)
            result_datetime = start_datetime + timedelta(minutes=minutes)
            return result_datetime.isoformat(timespec='minutes')
        except (ValueError, AttributeError) as e:
            return False
#------------------------- Запуск DB -------------------------
def wait_for_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.close()


def initialize_database():
    Base.metadata.create_all(bind=engine)


app = Flask(__name__)

with app.app_context():
    wait_for_db()
    initialize_database()

# ------------------------------------------------------- основные функции
@app.route('/api/check_availability', methods=['GET'])
def check_availability():
    st_time_str = request.args.get('start')
    en_time_str = request.args.get('end')
    duration = request.args.get('duration')

    # проверяем соответствие формату
    if not is_datetime(st_time_str):
        return error_response('неверный формат даты(начальное время)', 400)

    if duration:
        try:
            minutes = int(duration)
        except:
            minutes = str_time_to_minutes(duration)
        finally:
            if minutes == -1:
                return error_response('Неверный формат даты(продолжительность)', 400)
            en_time_str = add_minutes_to_datetime(st_time_str, minutes)

    if not is_datetime(en_time_str):
        return error_response('неверный формат даты(конечное время)', 400)

    try:
        seats = {
            i: True
            for i in range(1, 21)
        }
        all_bookings = get_bookings_by_datetime_range(st_time_str, en_time_str)
        occupied_places = set([b['id_place'] for b in all_bookings])
        for place in occupied_places:
            seats[int(place)] = False

        return jsonify({"seats": seats}), 200 # seats - ответ на вопрос "свободно ли место?" для каждого места
    except Exception as e:
        print(str(e))
        return error_response(str(e), 400)


@app.route('/api/booking', methods=['POST'])
def create_booking_():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    st_datetime_str = data.get('st_datetime')
    duration = data.get('duration')
    id_place = data.get('id_place')

    duration = str_time_to_minutes(duration)
    if duration == -1:
        return error_response('Неверный формат длительности брони', 400)
    if not is_datetime(st_datetime_str):
        return error_response('Неверный формат даты', 400)
    if not (username and password and duration and id_place):
        return error_response('Одно из обязательных полей не заполнено', 400)
    try:
        if int(duration)<0 or int(id_place) < 1 or int(id_place) > 20:
            return error_response('Недопустимые значения', 400)
    except: return error_response('Недопустимые значения', 400)

    sender_user = get_user(name=username, password=password)
    if not sender_user:
        return error_response('Пользователь с таким именем и паролем не найден', 404)

    response = requests.get('http://localhost:5000/api/check_availability',
        params={'start': st_datetime_str, 'duration': duration})
    if response.status_code != 200:
        print(response.json())
        return error_response('Не удалось проверить доступность места',400)
    if not response.json()['seats'].get(str(id_place), False):
        return error_response('Место уже занято',400)


    new_book = create_booking(id_user=sender_user['id'], id_place=id_place, datetime_str=st_datetime_str, duration_minutes=duration)
    if new_book:
        return jsonify({"message": "Место успешно забронировано"}), 201
    else:
        return error_response('Проблемы с созданием записи', 400)


# @app.route('/api/booking', methods=['GET'])
# def get_booking():
#     return
# @app.route('/api/booking', methods=['PUT'])
# def get_booking():
#     return
# @app.route('/api/booking', methods=['DELETE'])
# def get_booking():
#     return
# @app.route('/api/booking', methods=['POST'])
# def get_booking():
#     return

@app.route('/api/registration', methods=['POST'])
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



if __name__ == '__main__':
    app.run(debug=True)