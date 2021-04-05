import pytest
from book_library_app import create_app,db
from book_library_app.commands.db_manage_commands import add_data


#odpalenie części testów
#python -m pytest tests\test_authors.py
#python -m pytest -k "test_create_author" # 4 testy

@pytest.fixture()
def app():
    app=create_app('testing')

    with app.app_context():
        db.create_all()

    yield app #obiekt zwracamy do funkcji testujacej
    # po kazdym zadaniu czyszcze baze danych


    app.config['DB_FILE_PATH'].unlink(missing_ok=True)#usuwam plik, jesli nie znaleziony to bez wyjątku

#tworzenie testowego klienta
@pytest.fixture #jesli podam do funkcji to wykona sie odrazu przed aplikacja
def client(app):
    with app.test_client() as client:
        yield client #zwracam klienta


#rejestrowanie testowego użytkownika
@pytest.fixture
def user(client):
    user={ 'username': 'test',
           'password': '123456',
           'email': 'test@gmail.com'}

    client.post('/api/v1/auth/register',json=user)
    return user

#potrzebne do testowania funckji get current user
@pytest.fixture
def token(client,user):#fixture wywoływane są tylko raz "w jednym momencie"
    response= client.post('/api/v1/auth/login', json={
        'username': user['username'],
        'password': user['password']
    })

    return response.get_json()['token']


#dodanie przykładowych rekordów do bazy za pomocą wcześniej utworzoną funkcją
@pytest.fixture
def sample_data(app):
    runner=app.test_cli_runner()
    runner.invoke(add_data)


@pytest.fixture
def author():
    return{
        'first_name':'Adam',
        'last_name': 'Mickiewicz',
        'birth_date':'24-12-1798'
    }
