import re
import jwt
from flask import request, url_for, current_app,abort
from flask_sqlalchemy import DefaultMeta, BaseQuery
from functools import wraps
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.expression import BinaryExpression
from werkzeug.exceptions import UnsupportedMediaType
from typing import Tuple
# from datetime import datetime


#testowanie na stronie: https://regex101.com/
# birth_date[gte]birth_date[gt]birth_date[lte]birth_date[lt]birth_date
COMPARSION_OPERATORS_RE=re.compile(r'(.*)\[(gte|gt|lt|lte)\]')



def validate_json_content_type(func):
    @wraps(func)
    def wrapper (*args,**kwargs):
        data=request.get_json()
        if data is None:
            raise UnsupportedMediaType("Content type must be application/json")
        return func(*args, **kwargs)
    return wrapper #bez wywowalnia


def token_requred(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token=None
        auth= request.headers.get('Authorization')
        if auth:
            token= auth.split(' ')[1]
        if token is None:
            abort(401,description='Missing token, Please login or register')

        try:

            payload=jwt.decode(token,current_app.config.get('SECRET_KEY'),algorithms='HS256')
        except jwt.ExpiredSignatureError: #token stracił ważność #klasa dziedziczy po poniższej
            abort(401, description='Missing token, Please login to get new token')

        except jwt.InvalidTokenError:

            abort(401, description='Invalid token, Please login or register')

        else:
            return func(payload['user_id'], *args,**kwargs)
    return wrapper



def get_schema_args(model:DefaultMeta)->dict:
    schema_args={'many': True}
    fields=request.args.get('fields')
    if fields: #wybieram ktore argumenty wyswietlac, sa one rozdzielone przecinkiem
        schema_args['only']=[field for field in fields.split(',') if field in model.__table__.columns]
    return schema_args


def apply_order(model: DefaultMeta, query:BaseQuery)-> BaseQuery:
    sort_keys=request.args.get('sort') #z url
    if sort_keys:
        for key in sort_keys.split(','): #przegladam klucze sortowania i sprawdzam ktory z nich jest malejacy
            desc=False
            if key.startswith('-'): #jesli zaczynamy od -
                key=key[1:]
                desc=True
            column_attr=getattr(model, key, None)  #nazwa modelu, nazwa atrybutu string, none gdy nie mamy klucza

            if column_attr is not None:
                #sortuje po column_atr
                query=query.order_by(column_attr.desc()) if desc else query.order_by(column_attr)

    return query

def _get_filter_argument(column_name: InstrumentedAttribute,value:str, operator:str )-> BinaryExpression:
    #podstawiam operatory w filtrowaniu
    operator_mapping ={
        '==': column_name == value,
        'gte': column_name >= value,
        'gt': column_name > value,
        'lte': column_name <= value,
        'lt': column_name < value
    }
    return operator_mapping[operator]




def apply_filter(model: DefaultMeta,query: BaseQuery)-> BaseQuery:#, params: ImmutableDict
    for param, value in request.args.items(): #params.items():
        if param not in {'fields', 'sort', 'page','limit'}:#inne atrybuty niz uzyte wczesniej
            operator='=='
            match=COMPARSION_OPERATORS_RE.match(param)# jesli sie nie uda dopasowac to jest none
            if match is not None:
                param,operator = match.groups()


            column_attr=getattr(model,param,None)
            if column_attr is not None:
                value=model.additional_validation(param, value) #kazda zaimportowoana klasa musi miec taka funckje
                if value is None:
                    continue
                filter_argument=_get_filter_argument(column_attr, value, operator)
                #query =query.filter(column_attr==value)#przed dodaniem filtrowania gte
                query=query.filter(filter_argument)
    return query


def get_pagination(query: BaseQuery,func_name:str)-> Tuple[list,dict]:
    #paginacja czyli okreslanie limitu rekordow na poszczegolnych stronach
    #https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/

    #wyciagam wartosci
    page= request.args.get('page',1,type=int)
    limit = request.args.get('limit', current_app.config.get('PER_PAGE',5), type=int)
    #items zwraca klucz oraz wartosc
    params={key: value for key, value in request.args.items() if key !='page'} #wychwytuje wszystkie parametry oprucz page
    paginate_obj=query.paginate(page,limit,False)
    pagination={
        'total_pages': paginate_obj.pages,
        'total_records': paginate_obj.total,
        'current_page': url_for(func_name,page=page, **params)#tworze url dla nastepnych autorow

    }
    if paginate_obj.has_next: #jesli jest nastepna strona
        pagination['next_page']= url_for(func_name,page=page+1, **params) #zwracamy kolejna strone

    if paginate_obj.has_prev: #wprowadzamy nazwe blueprintu authors
        pagination['previous_page']= url_for(func_name,page=page-1, **params)

    return paginate_obj.items, pagination