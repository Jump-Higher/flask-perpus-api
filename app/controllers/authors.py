from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import select_all, select_by_id, order_by, filter_by, meta_data
from app.models.authors import Authors
from app.schema.authors_schema import AuthorsSchema
from flask import request
from app import response_handler,db
from uuid import UUID
from app.controllers.roles import user_auth
import os
  
@jwt_required()
def create_author():
    try:
        # Check Auth
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth(): 
            json_body = request.json
            
            # Checking errors with schema
            schema = AuthorsSchema() 
            errors = schema.validate(json_body)
            if errors and json_body['phone_number'] != "":
                return response_handler.bad_request(errors)
            else:
                for i in select_all(Authors):
                    if json_body['name'] == i.name:
                        return response_handler.bad_request("Author is Exist")
            
            new_author = Authors(name = json_body['name'],
                                email = json_body['email'],
                                gender = json_body['gender'],
                                phone_number = json_body['phone_number'],
                                )

            db.session.add(new_author)
            db.session.commit()
        
            data = schema.dump(new_author)
            return response_handler.created(data,"Author Successfull Created ")
        else:
            return response_handler.unautorized()
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')

    except Exception as err:
        return response_handler.bad_gateway(str(err))
    
@jwt_required() 
def author(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check id is UUID or not
            UUID(id)
            # Check Author is exist or not
            author = select_by_id(Authors, id)
            if author == None:
                return response_handler.not_found('Author not Found')
            
            # Add data to response 
            schema = AuthorsSchema()
            data = schema.dump(author)
            
            return response_handler.ok(data,"")
        else:
            return response_handler.unautorized()
        
    except ValueError:
        return response_handler.bad_request("Invalid Id")
        
    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()
def update_author(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check  id is UUID or not
            UUID(id)
            json_body = request.json
            
            # Check error with schema
            schema = AuthorsSchema()
            errors = schema.validate(json_body) 
            if errors and json_body['phone_number'] != "":
                return response_handler.bad_request(errors)
            
            # Check Author if not exist
            authors = select_by_id(Authors,id)
            if authors == None:
                return response_handler.not_found('Bookshelves not Found')
            
            # Check data of author same with previous or not 
            if all(json_body[field] == getattr(authors, field) for field in ['name','email','gender','phone_number']):
                return response_handler.bad_request("Author Already Updated")
            else:
                current_author = filter_by(Authors, 'name', json_body['name'])
                # Check author same with the others or not
                if current_author != None and authors.name != json_body['name']: 
                    return response_handler.conflict('Author is exist')
                
                # Add author to db
                authors.name = json_body['name']
                authors.email = json_body['email']
                authors.gender = json_body['gender']
                authors.phone_number = json_body['phone_number']
                db.session.commit()
                
                data = schema.dump(authors)
                 
                return response_handler.ok(data, "Author successfull updated")
        else:
            return response_handler.unautorized()

    except ValueError:
        return response_handler.bad_request("Invalid Id")
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()
def authors():
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Get param from url
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
            # Check is page exceed or not
            page_exceeded = meta_data(Authors,page,per_page)
            if page_exceeded: 
                return response_handler.not_found("Page Not Found") 
            
            # Query data authors all
            authors = order_by(Authors, 'page', page, 'per_page', per_page)
             # Iterate to data
            data = []
            for i in authors:
                data.append({
                    "id_author" : i.id_author,
                    "name" : i.name,
                    "email" : i.email,
                    "gender" : i.gender,
                    "phone_number" : i.phone_number,
                    "created_at": i.created_at,
                    "updated_at": i.updated_at
                })
                
            return response_handler.ok_with_meta(data, authors)
        else:
            return response_handler.unautorized()
        
    except Exception as err:
        return response_handler.bad_request(err)
            