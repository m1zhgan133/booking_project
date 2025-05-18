import pytest
from app import create_app
from interaction_with_db import *
from datetime import datetime, timedelta
from unittest.mock import patch
import os


@pytest.fixture(scope='module')
def test_app():
    TEST_DATABASE_URL = "postgresql://testuser:testpass@db_test:5432/testdb"
    os.environ['DATABASE_URL_TEST'] = TEST_DATABASE_URL
    os.environ['admin_password'] = 'testadminpass'
    os.environ['admin_username'] = 'testadmin'
    os.environ['TESTING'] = 'true'

    app = create_app({
        'TESTING': True,
        'DATABASE_URL': TEST_DATABASE_URL
    })

    with app.app_context():
        Base.metadata.create_all(bind=engine)

    yield app

    with app.app_context():
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope='module')
def client(test_app):
    return test_app.test_client()


@pytest.fixture(scope='function')
def db_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope='function')
def test_user(client, db_session):
    db_session.query(User).delete()
    db_session.commit()

    user_data = {
        'username': 'testuser',
        'password': 'testpass'
    }
    response = client.post('/api/user', json=user_data)
    assert response.status_code == 201

    user = get_user(name=user_data['username'], password=user_data['password'])
    yield user

    delete_user(user['id'])


@pytest.fixture(scope='function')
def test_booking(test_user, client):
    booking_data = {
        'username': test_user['name'],
        'password': 'testpass',
        'st_datetime': (datetime.now() + timedelta(hours=1)).isoformat(timespec='minutes'),
        'duration': '01:30',
        'id_place': 1
    }

    with patch('app.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"seats": {str(i): True for i in range(1, 21)}}
        mock_get.return_value.status_code = 200

        response = client.post('/api/booking', json=booking_data)
        assert response.status_code == 201

        # Получаем созданную бронь из БД
        bookings = get_all_bookings()
        booking_id = bookings[-1]['id']  # Берем последнюю запись

        yield booking_id

        # Удаление с явным указанием user_id владельца
        client.delete('/api/booking', json={
            'username': test_user['name'],
            'password': 'testpass',
            'booking_id': booking_id
        })