def test_admin_auth(client):
    response = client.post('/api/is_admin', json={
        'username': 'testadmin',
        'password': 'testadminpass'
    })
    assert response.status_code == 200

def test_non_admin_access(client):
    response = client.get('/api/booking', query_string={
        'request_type': 'all',
        'username': 'invaliduser',
        'password': 'invalidpass'
    })
    assert response.status_code == 401

# ---------------------------- GET ----------------------------
def test_get_booking(test_booking, client):
    response = client.get('/api/booking', query_string={
        'request_type': 'all',
        'username': 'testadmin',
        'password': 'testadminpass'
    })
    assert response.status_code == 200
    bookings = response.json
    assert isinstance(bookings, list)
    assert any(b['id'] == int(test_booking) for b in bookings)

# ---------------------------- DELETE ----------------------------

def test_NOT_admin_delete_user(test_user, client):
    response = client.delete('/api/user', json={
        'username': 'testuser',
        'password': 'testpass',
        'user_id': 1
    })
    assert response.status_code == 403