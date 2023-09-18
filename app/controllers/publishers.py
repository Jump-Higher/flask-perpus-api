from flask_jwt_extended import jwt_required, get_jwt_identity 
from app.models import select_all, select_by_id, filter_by, meta_data, order_by
from app.models.publishers import Publishers
from app.schema.publishers_schema import PublishersSchema
from flask import request
from app import response_handler,db
from uuid import UUID
from app.controllers import admin_auth, check_update, public_auth
import os

@jwt_required()
def create_publisher():
    try:
        # Check Auth
        current_user = get_jwt_identity()
        if current_user['id_role'] in admin_auth(): 
            json_body = request.json
            
            # Checking errors with schema
            schema = PublishersSchema() 
            errors = schema.validate(json_body)
            if errors:
                return response_handler.bad_request(errors)
            else:
                for i in select_all(Publishers):
                    if json_body['name'] == i.name:
                        return response_handler.bad_request_array('name','Publisher is Exist')
            
            new_publisher = Publishers(name = json_body['name'],
                                       email = json_body['email'], 
                                       phone_number = json_body['phone_number'])

            db.session.add(new_publisher)
            db.session.commit()
        
            data = schema.dump(new_publisher)
            return response_handler.created(data,"Publisher Successfull Created ")
        else:
            return response_handler.unautorized()
    
    except KeyError as err:
        return response_handler.bad_request_array(f'{err.args[0]}', f'{err.args[0]} field must be filled')

    except Exception as err:
        return response_handler.bad_gateway(str(err))
    
@jwt_required() 
def publisher(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in public_auth():
            # Check id is UUID or not
            UUID(id)
            # Check Publisher is exist or not
            publisher = select_by_id(Publishers, id)
            if publisher == None:
                return response_handler.not_found_array('id_publisher','Publisher not Found')
            
            # Add data to response 
            schema = PublishersSchema()
            data = schema.dump(publisher)
            
            return response_handler.ok(data,"")
        else:
            return response_handler.unautorized()
        
    except ValueError:
        return response_handler.bad_request_array('id_publisher','Invalid Id')
    
    except KeyError as err:
        return response_handler.bad_request_array(f'{err.args[0]}', f'{err.args[0]} field must be filled')

    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()
def update_publisher(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in admin_auth():
            # Check  id is UUID or not
            UUID(id)
            json_body = request.json
            
            # Check error with schema
            schema = PublishersSchema()
            errors = schema.validate(json_body) 
            if errors and json_body['phone_number'] != '':
                return response_handler.bad_request(errors)
            
            # Check Publisher if not exist
            publishers = select_by_id(Publishers,id)
            if publishers == None:
                return response_handler.not_found_array('publisher','Publisher not Found')
        
            #Check data of publisher same with previous or not 
            array = ['name','email','phone_number']
            
            if check_update(json_body, publishers, array) == True:
                return response_handler.bad_request_array('publisher','Publisher Already Updated')
            else:
                current_publisher = filter_by(Publishers, 'name', json_body['name'])
                # Check author same with the others or not
                if current_publisher != None and publisher.name != json_body['name']: 
                    return response_handler.conflict_array('name','Publisher is exist')
                
                # Add author to db
                publishers.name = json_body['name']
                publishers.email = json_body['email']
                publishers.phone_number = json_body['phone_number']
                db.session.commit()
                
                data = schema.dump(publishers)
                
                 
                return response_handler.ok(data, 'Publisher successfull updated')
        else:
            return response_handler.unautorized()

    except ValueError:
        return response_handler.bad_request_array('id_publisher','Invalid Id')

    except KeyError as err:
        return response_handler.bad_request_array(f'{err.args[0]}', f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()
def publishers():
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in admin_auth():
            # Get param from url
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
            # Check is page exceed or not
            page_exceeded = meta_data(Publishers,page,per_page)
            if page_exceeded: 
                return response_handler.not_found("Page Not Found") 
            
            # Query data publisher all
            publishers = order_by(Publishers, 'page', page, 'per_page', per_page)
             # Iterate to data
            data = []
            for i in select_all(Publishers):
                data.append(PublishersSchema().dump(i))
 
            return response_handler.ok_with_meta(data, publishers)
        else:
            return response_handler.unautorized()
        
    except Exception as err:
        return response_handler.bad_request(str(err))
            