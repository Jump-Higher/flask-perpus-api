from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import select_by_id, select_all, filter_by, meta_data, order_by
from flask import request
from app.schema.categories_schema import CategoriesSchema
from app import response_handler
from app.models.categories import Categories
from app import db
from app.controllers.roles import user_auth
from uuid import UUID
import os

@jwt_required()
def create_category():
    try: 
        # Check Auth
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth(): 
            json_body = request.json
            
            # Checking errors with schema
            schema = CategoriesSchema() 
            errors = schema.validate(json_body)
            if errors:
                return response_handler.bad_request(errors)
            else:
                for i in select_all(Categories):
                    if json_body['category'] == i.category:
                        return response_handler.conflict('Category is Exist')
                    
            new_category = Categories(category = json_body['category'])
                    
            db.session.add(new_category)
            db.session.commit()
        
            data = schema.dump(new_category)
            return response_handler.created(data,"Category Successfull Created ")
        else:
            return response_handler.unautorized()
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')

    except Exception as err:
        return response_handler.bad_gateway(str(err))
 
@jwt_required()
def category(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check id is UUID or not
            UUID(id)
            # Check Category is exist or not
            categories = select_by_id(Categories,id)
            if categories == None:
                return response_handler.not_found('Category not Found')
            
            # Add data to response 
            schema = CategoriesSchema()
            data = schema.dump(categories)
            
            return response_handler.ok(data,"")
        else:
            return response_handler.unautorized()
        
    except ValueError:
        return response_handler.bad_request("Invalid Id")
        
    except Exception as err:
        return response_handler.bad_gateway(str(err))
  
@jwt_required()
def update_category(id):
    try: 
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check  id is UUID or not
            UUID(id)
            json_body = request.json
            
            # Check error with schema
            schema = CategoriesSchema()
            errors = schema.validate(json_body) 
            if errors:
                return response_handler.bad_request(errors)
             
            # Check category if not exist
            categories = select_by_id(Categories,id)
            if categories == None:
                return response_handler.not_found('Category not Found')
            
            # Check name of category same with previous or not
            if json_body['category'] == categories.category: 
                return response_handler.bad_request("Your Category Already Updated")
            else:
                current_category = filter_by(Categories, 'category', json_body['category'])
                # Check category same with the others or not
                if current_category != None: 
                    return response_handler.conflict('Category is exist') 
                
                # Add category to db
                categories.category = json_body['category']  
                db.session.commit()

                return response_handler.ok("", "Category successfuly updated")
        else:
            return response_handler.unautorized()

    except ValueError:
        return response_handler.bad_request("Invalid Id")
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))
 
@jwt_required()
def categories():
    try:
        current_user = get_jwt_identity() 
        
        if current_user['id_role'] in user_auth():
            # Get param from url
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
            # Check is page exceed or not
            page_exceeded = meta_data(Categories,page,per_page)
            if page_exceeded: 
                return response_handler.not_found("Page Not Found") 
            
            # Query data categories all
            categories = order_by(Categories, 'page', page, 'per_page', per_page)
            
            # Iterate to data
            data = []
            for i in select_all(Categories):
                data.append(CategoriesSchema().dump(i))
 
            return response_handler.ok_with_meta(data, categories)
        else:
            return response_handler.unautorized()
        
    except Exception as err:
        return response_handler.bad_request(err)
 