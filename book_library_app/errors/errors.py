from book_library_app import db #,app
from flask import Response,jsonify
from book_library_app.errors import errors_bp

class ErrorResposne:
    def __init__(self,message:str,http_status:int):
        self.payload={
            'success':False,
            'message': message
        }
        self.http_status=http_status
    def to_response(self)->Response:
        response=jsonify(self.payload)
        response.status_code=self.http_status
        return response


#jesli cos jest nie tak ze zmiennymi
@errors_bp.app_errorhandler(400)
def bad_request_error(err):
    #inaczej wyciągam error ponieważ jest tworzony przez pakiet marshmallow
    messages=err.data.get('messages',{}).get('json',{})
    return ErrorResposne(messages, 400).to_response()

@errors_bp.app_errorhandler(404)
def not_found_error(err):
    return ErrorResposne(err.description, 404).to_response()


@errors_bp.app_errorhandler(401)
def unauthorized_error(err):
    return ErrorResposne(err.description, 401).to_response()

@errors_bp.app_errorhandler(409)
def conflict_error(err):
    return ErrorResposne(err.description, 409).to_response()

#w przypadku gdy content type nie jest zaznaczony
@errors_bp.app_errorhandler(415)
def unsupported_media_type_error(err):
    return ErrorResposne(err.description, 415).to_response()


@errors_bp.app_errorhandler(500)
def internal_server_error(err):
    db.session.rollback() #czyszczenie sesji w przypadku gdy problem powstanie na etapie wysylania query
    return ErrorResposne(err.description, 500).to_response()
