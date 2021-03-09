from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db=SQLAlchemy()
migrate=Migrate()

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name]) #wyciagam klucz development

    db.init_app(app)
    migrate.init_app(app,db)

    from book_library_app.commands import db_manage_bp
    from book_library_app.errors import errors_bp
    from book_library_app.authors import authors_bp
    from book_library_app.books import books_bp
    from book_library_app.auth import auth_bp
    app.register_blueprint(db_manage_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(authors_bp, url_prefix='/api/v1')
    app.register_blueprint(books_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

    return app

# from book_library_app import authors
# from book_library_app import models
# from book_library_app.commands import db_manage_commands
# #flask db-manage terminal
# from book_library_app import errors

# #wyswietlenie baz danych
# results=db.session.execute('show databases')#jezyk SQL
#
# for row in results:
#     print(row)



# endpoint poczatkowy
# @app.route('/')
# def index():
#     return "hello from flask"
