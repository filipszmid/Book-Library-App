import jwt
from book_library_app import db
from marshmallow import Schema, fields, validate,validates, ValidationError
from  datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash ,check_password_hash
from flask import current_app
# from flask_sqlalchemy import BaseQuery
# from flask import request, url_for
#
# # from werkzeug.datastructures import ImmutableDict
# from book_library_app import Config
# from typing import Tuple
# import re



class Author(db.Model):
    '''
    #a1= Author(first_name='jan',last_name='kowalski', birth_date=date(1998,1,1))
    #db.create_all()
    #db.session.add(a1)
    #db.session.commit()
    #Author.query.all()
    #db.drop_all()

    #mysql command line client
    #show tables;
    #select * from Authors;
    '''

    __tablename__='authors'
    id          =     db.Column(db.Integer, primary_key=True)
    first_name  =     db.Column(db.String(50),nullable=False)
    last_name   =     db.Column(db.String(50), nullable=False)
    birth_date  =     db.Column(db.Date,nullable=False)

    books= db.relationship('Book', back_populates='author', cascade='all, delete-orphan')
    #             nazwa argumentu z ktorym jest powiazany,  typ usuwania danych gdy usune authora to ksiazki sie tez usuna


    def __repr__(self):
        return f'<{self.__class__.__name__}>: {self.first_name} {self.last_name}'

    @staticmethod
    def additional_validation(param:str, value:str)->date:
        if param == 'birth_date':  # wyjatek jesli użytkownik poda zle dane do parametru birth date
            try:
                value = datetime.strptime(value, '%d-%m-%Y').date()
            except ValueError:
                value=None
        return value

# #przed przeniesieniem do pliku utils.py
#     @staticmethod
#     def apply_order(query:BaseQuery, sort_keys:str)-> BaseQuery:
#         if sort_keys:
#             for key in sort_keys.split(','): #przegladam klucze sortowania i sprawdzam ktory z nich jest malejacy
#                 desc=False
#                 if key.startswith('-'): #jesli zaczynamy od -
#                     key=key[1:]
#                     desc=True
#                 column_attr=getattr(Author, key, None)  #nazwa modelu, nazwa atrybutu string, none gdy nie mamy klucza
#
#                 if column_attr is not None:
#                     #sortuje po column_atr
#                     query=query.order_by(column_attr.desc()) if desc else query.order_by(column_attr)
#
#         return query







# class a(db.Model):
#     id


class Book(db.Model):
    '''Jak migrowac? : flask db migrate -m "books table
    flask db upgrade"'''
    __tablename__='books'
    id = db.Column(db.Integer,primary_key=True)
    title =db.Column(db.String(50),nullable=False)
    isbn =db.Column(db.BigInteger,nullable=False,unique=True)#wartosci unikatowe
    number_of_pages = db.Column(db.Integer, nullable=False)
    description= db.Column(db.Text)
    author_id= db.Column(db.Integer,db.ForeignKey('authors.id'),nullable=False)

    #nie reprezentuje kolumny tylko jest to powiazanie
    author= db.relationship('Author', back_populates='books')
    #to jest obiekt, mamy dostep do jego atrybutow zdefiniwoanych w klasie Author

    def __repr__(self):
        return f'{self.title} - {self.author.first_name} {self.author.last_name}'


    @staticmethod #nie potrzebujemy nic walidowac, ale w apply filter zakladamy ze mamy taka funkcje
    def additional_validation(param:str, value:str)->str:
        return value

class User(db.Model):
    '''flask db migrate -m "users table
    flask db upgrade"'''
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(255),nullable=False,unique=True,index=True)
    email=db.Column(db.String(255),nullable=False,unique=True)
    password=db.Column(db.String(255),nullable=False)
    creation_date=db.Column(db.DateTime, default=datetime.utcnow)#metoda call back bez nawiasow, aktualna data domyslnie

    #haszowanie hasla
    @staticmethod
    def generate_hashed_password(password:str)->str:
        return generate_password_hash(password)

    def is_password_valid(self,password:str)->bool:
        return check_password_hash(self.password,password)


    #data waznosci tokena i username
    def generate_jwt(self)->bytes:
        payload={
            'user_id':self.id,
            'exp': datetime.utcnow()+ timedelta(minutes=current_app.config.get('JWT_EXPIRED_MINUTES',30))
            #z aplikacji config sciagam ile minut ma byc wazny token i dodaje go do aktualnego czasu
        }
        return jwt.encode(payload,current_app.config.get('SECRET_KEY'))#obiekt byte


class UserSchema(Schema):
    #jwt.io tokeny
    id=fields.Integer(dump_only=True)
    username=fields.String(required=True,validate=validate.Length(max=255))
    email=fields.Email(required=True)
    password=fields.String(required=True,load_only=True,validate=validate.Length(min=6,max=255))
    creation_date=fields.DateTime(dump_only=True)



class AuthorSchema(Schema):
    #id wykorzystywane tylko podczas dump
    id          =   fields.Integer(dump_only=True)
    first_name  =   fields.String(required=True,validate=validate.Length(max=50))
    last_name   =   fields.String(required=True,validate=validate.Length(max=50))
    birth_date  =   fields.Date('%d-%m-%Y',required=True)

    #wyswietlanie ksiazek nalezacych do autora w get all authors, lista bo moze byc kilka ksiazek
    books=fields.List(fields.Nested(lambda : BookSchema(exclude=['author'])))


    @validates('birth_date')
    def validate_birth_date(self,value):
        #sprawdzam czy data jest mniejsza niz aktualna
        if value > datetime.now().date():
            #raise ValidationError(f'Birth date must be lower than {datetime.now().date()}')
            raise ValidationError('Birth date must be lower than')




class BookSchema(Schema):
    #id wykorzystywane tylko podczas dump
    id          =   fields.Integer(dump_only=True)
    title  =   fields.String(required=True,validate=validate.Length(max=50))
    isbn   =   fields.Integer(required=True)
    number_of_pages = fields.Integer(required=True)
    description= fields.String()
    author_id=fields.Integer(load_only=True) #autor id nie bedzie ywkorzystywane w przypadku metody dump
    author= fields.Nested(lambda: AuthorSchema(only=['id','first_name','last_name']))

    @validates('isbn')
    def validate_isbn(self,value):
        if len(str(value))!=13:
            raise ValidationError('ISBN must contains 13 digits')


class UserPasswordUpdateSchema(Schema):
    current_password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))
    new_password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))


author_schema=AuthorSchema()
book_schema=BookSchema()
user_schema=UserSchema()
user_password_update_schema=UserPasswordUpdateSchema