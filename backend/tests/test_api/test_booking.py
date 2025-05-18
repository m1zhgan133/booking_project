from unittest.mock import patch
from datetime import datetime, timedelta
# ---------------------------- CREATE ----------------------------

def test_create_wrong_duration(test_booking, test_user, client):
    response = client.post('/api/booking', json={
        'username': test_user['name'],
        'password': 'testpass',
        'st_datetime': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '01:302', # ошибка
        'id_place': 1
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == "Неверный формат длительности брони"

# ----------------------------

def test_create_miss_field_password(test_booking, test_user, client):
    response = client.post('/api/booking', json={
        'username': test_user['name'],
        'st_datetime': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '01:30',
        'id_place': 1
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == 'Одно из обязательных полей не заполнено'


def test_create_miss_field_name(test_booking, test_user, client):
    response = client.post('/api/booking', json={
        'password': 'testpass',
        'st_datetime': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '01:30',
        'id_place': 1
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == 'Одно из обязательных полей не заполнено'


def test_create_miss_field_id(test_booking, test_user, client):
    response = client.post('/api/booking', json={
        'username': test_user['name'],
        'password': 'testpass',
        'st_datetime': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '01:30',
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == 'Одно из обязательных полей не заполнено'

# ----------------------------

def test_create_minus_duration(test_booking, test_user, client):
    response = client.post('/api/booking', json={
        'username': test_user['name'],
        'password': 'testpass',
        'st_datetime': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '-01:30',
        'id_place': 1
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == 'Неверный формат длительности брони'


def test_create_minus_id(test_booking, test_user, client):
    response = client.post('/api/booking', json={
        'username': test_user['name'],
        'password': 'testpass',
        'st_datetime': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '01:30',
        'id_place': -1
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == 'Недопустимые значения'


def test_create_dig_id(test_booking, test_user, client):
    response = client.post('/api/booking', json={
        'username': test_user['name'],
        'password': 'testpass',
        'st_datetime': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '01:30',
        'id_place': 21
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == 'Недопустимые значения'

# ----------------------------

def test_create_not_exist_name(test_booking, test_user, client):
    response = client.post('/api/booking', json={
        'username': '123', # ошибка
        'password': 'testpass',
        'st_datetime': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '01:30',
        'id_place': 1
    })
    assert response.status_code == 404
    assert response.get_json()["error"] == 'Пользователь с таким именем и паролем не найден'


def test_create_not_exist_password(test_booking, test_user, client):
    response = client.post('/api/booking', json={
        'username': test_user['name'],
        'password': '123', # ошибка
        'st_datetime': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '01:30',
        'id_place': 1
    })
    assert response.status_code == 404
    assert response.get_json()["error"] == 'Пользователь с таким именем и паролем не найден'


# ---------------------------- GET --------------------------------------------------------

def test_get_booking_range_with_duration(test_booking, test_user, client):
    response = client.get('/api/booking', query_string={
        'request_type': 'range',
        'username': test_user['name'],
        'password': 'testpass',
        'start': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '01:30'
    })
    assert response.status_code == 200

def test_get_booking_range_with_end(test_booking, test_user, client):
    response = client.get('/api/booking', query_string={
        'request_type': 'range',
        'username': test_user['name'],
        'password': 'testpass',
        'start': (datetime.now() + timedelta(minutes=50)).isoformat(timespec='minutes'),
        'duration': '01:30'
    })
    assert response.status_code == 200

# ----------------------------

def test_get_booking_one(test_booking, test_user, client):
    response = client.get('/api/booking', query_string={
        'request_type': None,  # ошибка
        'username': test_user['name'],
        'password': 'testpass'
    })
    assert response.status_code == 501
    assert response.get_json()["error"] == 'Функция пока не реализованна'


def test_get_booking_wrong_request_type(test_booking, test_user, client):
    response = client.get('/api/booking', query_string={
        'request_type': 'pivo', # ошибка
        'username': test_user['name'],
        'password': 'testpass'
    })
    assert response.status_code == 400
    assert response.get_json()["error"] == 'Некорректный тип запроса'


# ---------------------------- PATCH ----------------------------

def test_update_booking(test_booking, test_user, client):
    new_data = {
        'booking_id': test_booking,
        'username': test_user['name'],
        'password': 'testpass',
        'place': 5,
        'start': (datetime.now()).isoformat(timespec='minutes'),
        'duration': '02:00'
    }
    response = client.patch('/api/booking', json=new_data)
    print(response.get_json())
    assert response.status_code == 200


# ---------------------------- DELETE ----------------------------

def test_delete_booking(test_booking, client, test_user):
    response = client.delete('/api/booking', json={
        'username': test_user['name'],
        'password': 'testpass',
        'booking_id': test_booking
    })
    assert response.status_code == 204