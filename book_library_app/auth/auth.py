from flask import abort,jsonify
import jwt
from webargs.flaskparser import use_args
from book_library_app.auth import auth_bp
from book_library_app.models import user_schema, User, UserSchema ,user_password_update_schema
from book_library_app.utils import validate_json_content_type, token_requred
from book_library_app import db


@auth_bp.route('/register', methods=['POST'])
@validate_json_content_type
@use_args(user_schema,error_status_code=400)
def register(args:dict):
    if User.query.filter(User.username==args['username']).first():
        abort(409, description=f'User with username {args["username"]} already exists')
    if User.query.filter(User.email==args['email']).first():
        abort(409, description=f'User with email {args["username"]} already exists')

    args['password']=User.generate_hashed_password(args['password'])
    user=User(**args)

    db.session.add(user)
    db.session.commit()

    token = user.generate_jwt()

    return jsonify({
        'success': True,
        'token': token
    }),201


@auth_bp.route('/login', methods=['POST'])
@validate_json_content_type
@use_args(UserSchema(only=['username','password']),error_status_code=401)
def login(args:dict):
    user=User.query.filter(User.username==args['username']).first()
    if not user:   #jesli nie zostal znaleziony
        abort(401, description='Invalid credentials')
    if not user.is_password_valid(args['password']): #sprawdzam czy jest poprawne haslo
        abort(401, description='Invalid credentials')

    token = user.generate_jwt()

    return jsonify({
        'success': True,
        'token': token
    })


@auth_bp.route('/me',methods=['GET'])
@token_requred
def get_current_user(user_id: int): #ctr shif e - zmiana w calym projekcie
    user=User.query.get_or_404(user_id,description=f'User with ide {user_id} not found')

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)

    })



@auth_bp.route('/update/password',methods=['PUT'])
@token_requred
@validate_json_content_type
@use_args(user_password_update_schema,error_status_code=400)
def update_password(user_id: int,args:dict): #ctr shif r  - zmiana w calym projekcie
    user=User.query.get_or_404(user_id,description=f'User with ide {user_id} not found') #szukam usera

    if not user.is_password_valid(args['current_password']): #sprawdzamy czy haslo jest poprawne
        abort(401,description='Invalid password')

    user.password=user.generate_hashed_password(args['new_password'])#haszuje nowe hasło
    db.session.commit()

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)

    })




@auth_bp.route('/update/data',methods=['PUT'])
@token_requred
@validate_json_content_type
@use_args(UserSchema(only=['username','email']),error_status_code=400)
def update_user_data(user_id: int,args:dict):
    if User.query.filter(User.username==args['username']).first():
        abort(409, description=f'User with username {args["username"]} already exists')
    if User.query.filter(User.email==args['email']).first():
        abort(409, description=f'User with email {args["email"]} already exists')

    print("koniec")

    user=User.query.get_or_404(user_id,description=f'User with ide {user_id} not found') #szukam usera

    #aktualizacja danych
    user.username=args['username']
    user.email=args['email']
    db.session.commit()

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)

    })