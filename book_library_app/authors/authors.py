from flask import jsonify #,request
from book_library_app import  db# ,app
from book_library_app.models import Author, AuthorSchema, author_schema
from webargs.flaskparser import use_args
from book_library_app.utils import validate_json_content_type, get_schema_args, apply_order,apply_filter ,get_pagination, token_requred
from book_library_app.authors import authors_bp


#wczesniej app po blueprint zmiana
@authors_bp.route('/authors', methods=['GET'])
def get_authors():
    #postman {{URL}}/api/v1/authors

    #authors = Author.query.all()
    #author_schema = AuthorSchema(many=True)
    #print(authors)

    #nowa funckjonalnosc, zwracamy tylko czesc pól
    query=Author.query
    schema_args=get_schema_args(Author)
    query=apply_order(Author,query)
    query = apply_filter(Author,query)  #filtrowanie danych #, request.args przed poprawka z immunit dict

    #paginaticja
    items, pagination =get_pagination(query,'authors.get_authors')

    authors=AuthorSchema(**schema_args).dump(items)


    # przed dodaniem paginacji
    #authors=query.all()
    #author_schema=AuthorSchema(**schema_args)

    return jsonify({
     'success': True,
     'data': authors, #author_schema.dump(authors)
     'number_of_records': len(authors),
     'pagination': pagination
    })



@authors_bp.route('/authors/<int:author_id>', methods=['GET'])

def get_author(author_id: int):
    author = Author.query.get_or_404(author_id, description=f'Author with id {author_id} not found')

    return jsonify({
     'success': True,
     'data': author_schema.dump(author)
    })




@authors_bp.route('/authors', methods=['POST'])
@token_requred
@validate_json_content_type
@use_args(author_schema,error_status_code=400)
def create_authors(user_id: int,args: dict):
    #nasze argumenty rekordu
    print(args)

    author=Author(**args)
    db.session.add(author)
    db.session.commit()


    #pierwszy sposob:
    #data=request.get_json()
    # first_name=data.get('first_name')
    # last_name=data.get('last_name')
    # birth_date=data.get('birth_date')
    # author= Author(first_name=first_name,last_name=last_name,birth_date=birth_date)
    #
    #
    # #dodawanie do bazy
    # db.session.add(author)
    # db.session.commit()
    # print(author)

    return jsonify({
     'success': True,
     'data': author_schema.dump(author)
    }), 201



@authors_bp.route('/authors/<int:author_id>', methods=['PUT'])
@token_requred
@validate_json_content_type
@use_args(author_schema,error_status_code=400) #zmiana na inny kod bledu
def update_author(user_id: int,args: dict, author_id: int):
    author = Author.query.get_or_404(author_id, description=f'Author with id {author_id} not found')


    author.first_name= args['first_name']
    author.last_name = args['last_name']
    author.birth_date = args['birth_date']

    db.session.commit()


    return jsonify({
     'success': True,
     'data': author_schema.dump(author) #f'Author with id:{author_id} has been updated.'
    })


@authors_bp.route('/authors/<int:author_id>', methods=['DELETE'])
@token_requred
def delete_author(user_id: int,author_id: int):
    #wyciagniecie autora z bazy
    author = Author.query.get_or_404(author_id, description=f'Author with id {author_id} not found')
    db.session.delete(author)
    db.session.commit()


    return jsonify({
     'success': True,
     'data': f'Author with id:{author_id} has been deleted.'
    })




