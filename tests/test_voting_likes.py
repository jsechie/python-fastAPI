
def test_vote_on_post(auth_client, test_post):
    data = {"post_id": test_post['Post']['id'], "dir": 1}
    response = auth_client.post('/votes', json=data )
    assert response.status_code == 201
    assert response.json().get('message') == "successfully voted"

def test_voting_twice(auth_client, test_post):
    data = {"post_id": test_post['Post']['id'], "dir": 1}
    auth_client.post('/votes', json=data )
    response = auth_client.post('/votes', json=data )
    assert response.status_code == 409

def test_deleting_vote(auth_client, test_post):
    data = {"post_id": test_post['Post']['id'], "dir": 1}
    data2 = {"post_id": test_post['Post']['id'], "dir": 0}
    auth_client.post('/votes', json=data )
    response = auth_client.post('/votes', json=data2 )
    assert response.status_code == 201

def test_deleting_vote_not_found(auth_client, test_post):
    data = {"post_id": test_post['Post']['id'], "dir": 0}
    response = auth_client.post('/votes', json=data )
    assert response.status_code == 404

def test_voting_post_not_found(auth_client, test_post):
    data = {"post_id": test_post['Post']['id'], "dir": 0}
    response = auth_client.post('/votes', json=data )
    assert response.status_code == 404