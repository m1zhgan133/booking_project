# ---------------------------- CREATE ----------------------------
def test_user_creation(client):
    response = client.post('/api/user', json={
        'username': 'newuser',
        'password': 'newpass'
    })
    assert response.status_code == 201
    assert 'newuser' in response.json['message']

def test_duplicate_user_creation(client):
    client.post('/api/user', json={'username': 'testuser', 'password': 'testpass'})

    response = client.post('/api/user', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 400

# ---------------------------- GET ----------------------------
def test_get_user_info(test_user, client):
    response = client.get('/api/user', query_string={
        'username': test_user['name'],
        'password': 'testpass'
    })
    assert response.status_code == 200

# ---------------------------- PATCH ----------------------------
def test_user_update(test_user, client):
    response = client.patch('/api/user', json={
        'username': test_user['name'],
        'password': 'testpass',
        'new_username': 'updated_user',
        'new_password': 'newpass123'
    })
    assert response.status_code == 403

# ---------------------------- DELETE ----------------------------
def test_delete_update(test_user, client):
    response = client.delete('/api/user', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 403
