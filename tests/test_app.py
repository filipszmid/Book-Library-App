from flask import Flask




def test_app(app):#obiekt sie odpali i mamy do niego dostęp
    assert isinstance(app,Flask) # sprawdzam czy to prawda
    assert app.config['TESTING'] is True
    assert app.config['DEBUG'] is True

#python -m pytest #uruchomienie modułu testującego








