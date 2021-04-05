import pytest


#testy zwiazane z blueprintem auth
# python -m pytest


def test_registration(client):
    response = client.post('/api/v1/auth/register',
                           json={
                               'username': 'tewest',
                               'password': '123456',
                               'email': 'test@gmail.com'

                           })
    response_data=response.get_json() #wyciągam dane zwrócone przez server
    assert response.status_code==201 #sprawdzam kod zwrotu
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    assert response_data['token'] #sprawdzam czy dostałem token

@pytest.mark.parametrize(
    'data,missing_field',
    [
        ({'username': 'test', 'password':'123456'},'email'),
        ({'username': 'test', 'email': 'test@gmail.com'}, 'password'),
        ({'password': '123456', 'email': 'test@gmail.com'}, 'username'),
    ]
 ) #przesłanie kilku danych wejściowych, uruchamiam funkcję dla różnych danych


#informacje zwracane w przypadku przeslania błednego zapytania
def test_registration_invalid_data(client, data, missing_field):
    #3 scenariusze - pominięty email, password, username
    response = client.post('/api/v1/auth/register',
                           json=data)
    response_data = response.get_json()
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data
    assert missing_field in response_data['message'] #sprawdzam czy w ciele odpowiedzi serwera znajduje się poprwany klucz, którego nie podaliśmy
    assert 'Missing data for required field.' in response_data['message'][missing_field]



def test_registration_invalid_content_type(client):
    #błedny typ danych
    response = client.post('/api/v1/auth/register',
                           data={
                               'username': 'tewest',
                               'password': '123456',
                               'email': 'test@gmail.com'

                           })
    response_data = response.get_json()
    assert response.status_code == 415
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data

def test_registration_already_used_username(client,user):
    response = client.post('/api/v1/auth/register',
                           json={
                               'username': user['username'],#taki sam username
                               'password': '123456',
                               'email': 'test123@gmail.com'#inny email

                           })
    response_data = response.get_json()
    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data

def test_registration_already_used_email(client,user):
    response = client.post('/api/v1/auth/register',
                           json={
                               'username':'name',
                               'password': '123456',
                               'email': user['email']

                           })
    response_data = response.get_json()
    assert response.status_code == 409
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'token' not in response_data


def test_get_current_user(client,user,token):
    response = client.get('/api/v1/auth/me',
                           headers={'Authorization': f'Bearer {token}'
                           })#ustawiam nagłówek authorization z wartościa tokena
    response_data=response.get_json() #wyciągam dane zwrócone przez server
    assert response.status_code==200 #sprawdzam kod zwrotu
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is True
    # funkcja current user zwraca informacie w nagłówku data, chcę sprawdzić te informacje
    assert response_data['data']['username']==user['username']
    assert response_data['data']['email'] == user['email']

    assert 'id' in response_data['data']
    assert 'creation_date' in response_data['data']


#nie zamieszczenie tokena
def test_get_current_user_missing_token(client):
    response = client.get('/api/v1/auth/me')
    response_data=response.get_json()
    assert response.status_code==401
    assert response.headers['Content-Type'] == 'application/json'
    assert response_data['success'] is False
    assert 'data' not in response_data

