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
admin_password = os.getenv("admin_password")
admin_username = os.getenv("admin_username")

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


def is_user_data_correct(username, password):
    """Проверяет наличие и длину"""
    if not username or not password:
        return "Имя и пароль обязательны", 400
    if len(username) > 100 or len(password) > 100:
        return "Имя или пароль слишком длинные(Максимальная длина - 100 символов)", 400
    return '', 200

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


# ---------------------------- booking ----------------------------
@app.route('/api/booking', methods=['POST'])
def create_booking_():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    st_datetime_str = data.get('st_datetime')
    duration = data.get('duration')
    id_place = data.get('id_place')

    user_id = data.get('user_id')


    duration = str_time_to_minutes(duration)
    if duration == -1:
        return error_response('Неверный формат длительности брони', 400)
    if not is_datetime(st_datetime_str):
        return error_response('Неверный формат даты', 400)
    if not (username and password and duration and id_place):
        return error_response('Одно из обязательных полей не заполнено', 400)
    try:
        if int(duration)<=0 or int(id_place) < 1 or int(id_place) > 20:
            return error_response('Недопустимые значения', 400)
    except: return error_response('Недопустимые значения', 400)

    # проверка на админа
    if user_id and is_admin(username, password):
        sender_user = get_user(id=user_id, is_admin=True)
    else:
        sender_user = get_user(name=username, password=password)

    if not sender_user:
        return error_response('Пользователь с таким именем и паролем не найден', 404)

    response = requests.get('http://localhost:5000/api/booking',
        params={'start': st_datetime_str, 'duration': duration, 'request_type':'range'})
    print(response.json())
    if response.status_code != 200:
        return error_response('Не удалось проверить доступность места',400)
    if not response.json()['seats'].get(str(id_place), False):
        return error_response('Место уже занято на это время',400)

    new_book = create_booking(id_user=sender_user['id'], id_place=id_place, datetime_str=st_datetime_str, duration_minutes=duration)
    if new_book:
        return jsonify({"message": "Место успешно забронировано"}), 201
    else:
        return error_response('Проблемы с созданием записи', 400)



@app.route('/api/booking', methods=['GET'])
def get_booking_():
    request_type = request.args.get('request_type')  # значения: all, range, None - 1 объект

    if request_type not in ('range', 'all', None):
        return error_response('Некорректный тип запроса', 400)

    if request_type and request_type == 'all':
        username = request.args.get('username')
        password = request.args.get('password')
        if is_admin(username, password):
            all_bookings = get_all_bookings()
            return jsonify(all_bookings), 200

    if request_type and request_type == 'range':
        st_time_str = request.args.get('start')
        en_time_str = request.args.get('end')
        duration = request.args.get('duration')
        not_include_id = request.args.get('not_include_id', -1)

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
            all_bookings = get_bookings_by_datetime_range(st_time_str, en_time_str, not_include_id=not_include_id)
            occupied_places = set([b['id_place'] for b in all_bookings])
            for place in occupied_places:
                seats[int(place)] = False

            return jsonify({"seats": seats}), 200 # seats - ответ на вопрос "свободно ли место?" для каждого места
        except Exception as e:
            return error_response(str(e), 400)

    elif not request_type: return error_response('Функция пока не реализованна', 501)


@app.route('/api/booking', methods=['PATCH'])
def update_booking_():
    data = request.get_json()
    booking_id = data.get('booking_id')
    username = data.get('username')
    password = data.get('password')

    id_place = data.get('place')
    st_datetime = data.get('start')
    duration = data.get('duration')
    #                                       проверки
    # проверяем дату и продолжительность
    if duration:
        try:
            duration = str_time_to_minutes(duration)
            if duration == -1:
                return error_response('Неверный формат длительности брони', 400)
            if not is_datetime(st_datetime):
                return error_response('Неверный формат даты', 400)
            if not (not duration and (duration != 0)) and int(duration)<=0:
                return error_response('Недопустимые значения продолжительности', 400)
        except:
            return error_response('Недопустимые значения продолжительности', 400)
    # проверяем корректность duration, id_place и booking_id
    try:
        if id_place and (int(id_place) < 1 or int(id_place) > 20):
            return error_response('Недопустимые значения номера места', 400)
        int(booking_id)
    except: return error_response('Недопустимые значения', 400)

    # проверяем свободность места для новых данных
    response = requests.get('http://localhost:5000/api/booking',
                            params={'start': st_datetime, 'duration': duration, 'request_type': 'range', 'not_include_id': booking_id})
    if response.status_code != 200:
        return error_response('Не удалось проверить доступность места', 400)
    if not response.json()['seats'].get(str(id_place), False):
        return error_response('Место уже занято на это время', 400)

    # проверяем корректность username и password
    m, code = is_user_data_correct(username, password)
    if code != 200:
        return error_response(m, code)

    # Проверяем существует ли такой user и обновляем
    user = get_user(name=username, password=password)
    if (user and user['name'] == username and user['password'] == password) or is_admin(username, password):
        is_updated = update_booking(booking_id, {
            'id_place': id_place,
            'st_datetime': st_datetime,
            'duration': duration
        })
        if is_updated:
            return jsonify({"message": "Бронь успешно отредактирована"}), 200
        else:
            return error_response('Проблемы с редактировнанием брони', 400)
    else:
        return error_response('Пользователь с такими данными не найден', 404)



@app.route('/api/booking', methods=['DELETE'])
def delete_booking():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    booking_id = data.get('booking_id')

    m, code = is_user_data_correct(username, password)
    if code != 200:
        return error_response(m, code)

    # Проверяем существует ли такой user
    user = get_user(name=username, password=password)
    if (user and user['name'] == username and user['password'] == password) or is_admin(username, password):
        if delete_booking_by_id(booking_id):
            return jsonify({"message": 'Пользователь был успешно удален'}), 204
        else:
            return error_response('Бронь с таким id не найдена', 404)
    else:
        return error_response('Пользователь с такими данными не найден', 404)



# ---------------------------- user ----------------------------
@app.route('/api/user', methods=['POST'])
def create_user_():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not data:
        return error_response("Нет данных, отправьте username и пароль", 400)

    m, code = is_user_data_correct(username, password)
    if code != 200:
        return error_response(m, code)

    # Проверяем уникальность username
    all_users = get_all_users()
    for u in all_users:
        if u['name'] == username:
            return error_response('Пользователь с таким именем уже существует', 400)

    create_user(
        name=username,
        password=password
    )
    return jsonify({"message": f"Пользователь {username} был успешно создан"}), 201


@app.route('/api/user', methods=['GET'])
def get_user_():
    request_type = request.args.get('request_type')  # значения: all, range, None - 1 объект

    if request_type not in ('all', None):
        return error_response('Некорректный тип запроса', 400)

    if request_type and request_type == 'all':
        username = request.args.get('username')
        password = request.args.get('password')
        if is_admin(username, password):
            all_users = get_all_users(password)
            return jsonify(all_users), 200

    if not request_type:
        username = request.args.get('username')
        password = request.args.get('password')

        m, code = is_user_data_correct(username, password)
        if code != 200:
            return error_response(m, code)

        # Проверяем существует ли такой user
        user = get_user(name=username, password=password)
        if user and user['name'] == username and user['password'] == password:
            # должно быть достаточно только усл. user, но я на всякий добавил доп проверки
            return jsonify(user), 200
        else:
            return error_response('Пользователь с такими данными не найден', 404)

@app.route('/api/user', methods=['PATCH'])
def update_user_():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username and password and is_admin(username, password):
        user_id = data.get('user_id')
        try:
            if int(user_id) < 0:
                return error_response('Неккорктный user_id', 400)
        except: return error_response('Неккорктный user_id', 400)

        update_data = {
            'name': data.get('new_username'),
            'password': data.get('new_password')
        }

        # проверка уникальности
        all_users = get_all_users()
        for u in all_users:
            if u['name'] == update_data['name']:
                return error_response('Пользователь с таким именем уже существует', 400)

        if update_user(user_id, update_data):
            return jsonify({'message': 'Данные пользователя успешно обновленны'}), 200
        else:
            return error_response('Проблемы с обновлением пользователя',400)


@app.route('/api/user', methods=['DELETE'])
def delete_user_():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username and password and is_admin(username, password):
        user_id = data.get('user_id')
        try:
            if int(user_id) < 0:
                return error_response('Неккорктный user_id', 400)
        except: return error_response('Неккорктный user_id', 400)

        if delete_user(user_id):
            return jsonify({'message': 'Пользователь успешно удален'}), 204
        else:
            return error_response('Проблемы с обновлением пользователя',400)
# ---------------------------- admin check ----------------------------
def is_admin(username, password):
    try:
        if password == admin_password and username == admin_username:
            return True
        else:
            return False
    except:
        return False # некорректный ввод

@app.route('/api/is_admin', methods=['POST'])
def is_admin_():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if is_admin(username, password):
        return jsonify({'message': 'Вы успешно авторизованы под учетной записью админа'})
    else:
        return error_response('Неверный username или пароль', 401)



if __name__ == '__main__':
    app.run(debug=True)