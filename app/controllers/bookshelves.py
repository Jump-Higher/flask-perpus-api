import os
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID
from app import db, response_handler
from app.controllers.roles import user_auth
from app.models import select_by_id, select_all, filter_by, order_by, meta_data
from app.models.bookshelves import Bookshelves 
from app.schema.bookshelves_schema import BookshelvesSchema
 
@jwt_required()
def create_bookshelf():
    try: 
        # Check Auth
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth(): 
            json_body = request.json
            
            # Checking errors with schema
            schema = BookshelvesSchema() 
            errors = schema.validate(json_body)
            if errors:
                return response_handler.bad_request(errors)
            else:
                for i in select_all(Bookshelves):
                    if json_body['bookshelf'] == i.bookshelf:
                        return response_handler.conflict('Bookshelf is Exist')
                    
            new_bookshelf = Bookshelves(bookshelf = json_body['bookshelf'])
                    
            db.session.add(new_bookshelf)
            db.session.commit()
        
            data = schema.dump(new_bookshelf)
            return response_handler.created(data,"Bookshelf Successfull Created ")
        else:
            return response_handler.unautorized()
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')

    except Exception as err:
        return response_handler.bad_gateway(str(err))
 
@jwt_required()
def bookshelf(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check id is UUID or not
            UUID(id)
            # Check Bookshelf is exist or not
            bookshelves = select_by_id(Bookshelves,id)
            if bookshelves == None:
                return response_handler.not_found('Bookshelves not Found')
            
            # Add data to response 
            schema = BookshelvesSchema()
            data = schema.dump(bookshelves)
            
            return response_handler.ok(data,"")
        else:
            return response_handler.unautorized()
        
    except ValueError:
        return response_handler.bad_request("Invalid Id")
        
    except Exception as err:
        return response_handler.bad_gateway(str(err))
  
@jwt_required()
def update_bookshelf(id):
    try: 
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check  id is UUID or not
            UUID(id)
            json_body = request.json
            
            # Check error with schema
            schema = BookshelvesSchema()
            errors = schema.validate(json_body) 
            if errors:
                return response_handler.bad_request(errors)
             
            # Check bookshelf if not exist
            bookshelves = select_by_id(Bookshelves,id)
            if bookshelves == None:
                return response_handler.not_found('Bookshelves not Found')
            
            # Check name of bookshelf same with previous or not
            if json_body['bookshelf'] == bookshelves.bookshelf: 
                return response_handler.bad_request("Your Bookshelf Already Updated")
            else:
                current_bookshelf = filter_by(Bookshelves, 'bookshelf', json_body['bookshelf'])
                # Check bookshelf same with the others or not
                if current_bookshelf != None: 
                    return response_handler.conflict('Bookshelf is exist') 
                
                # Add bookshelf to db
                bookshelves.bookshelf = json_body['bookshelf']  
                db.session.commit()

                return response_handler.ok("", "Bookshelf successfuly updated")
        else:
            return response_handler.unautorized()

    except ValueError:
        return response_handler.bad_request("Invalid Id")
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))
 
@jwt_required()
def bookshelves():
    try:
        current_user = get_jwt_identity() 
        
        if current_user['id_role'] in user_auth():
            
            # Get param from url
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
            # Check is page exceed or not
            page_exceeded = meta_data(Bookshelves,page,per_page)
            if page_exceeded: 
                return response_handler.not_found("Page Not Found") 
            
            # Query data bookshelves all
            bookshelves = order_by(Bookshelves, 'page', page, 'per_page', per_page)
            
            # Iterate to data
            data = []
            for i in bookshelves:
                data.append({
                    "id_bookshelf" : i.id_bookshelf,
                    "bookshelf" : i.bookshelf,
                    "created_at": i.created_at,
                    "updated_at": i.updated_at
                })
                
            return response_handler.ok_with_meta(data, bookshelves)
        else:
            return response_handler.unautorized()
        
    except Exception as err:
        return response_handler.bad_request(err)