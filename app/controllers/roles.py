
from app.models import select_users_role
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import select_by_id, select_all, filter_by, meta_data, order_by
from flask import request
from app.schema.roles_schema import RolesSchema
from app import response_handler
from app.models.roles import Roles
from app import db 
from uuid import UUID
import os

# CRUL
def user_auth():
    authorized_roles = str({select_users_role('SUPER_ADMIN_ROLE'), 
                            select_users_role('ADMIN_ROLE')})
    return authorized_roles

@jwt_required()
def create_role():
    try: 
        # Check Auth
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth(): 
            json_body = request.json
            
            # Checking errors with schema
            schema = RolesSchema() 
            errors = schema.validate(json_body)
            if errors:
                return response_handler.bad_request(errors)
            else:
                for i in select_all(Roles):
                    if json_body['name'] == i.name:
                        return response_handler.conflict('Role is Exist')
                    
            new_role = Roles(name = json_body['name'])
                    
            db.session.add(new_role)
            db.session.commit()
        
            data = schema.dump(new_role)
            return response_handler.created(data,"Role Successfull Created ")
        else:
            return response_handler.unautorized()
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')

    except Exception as err:
        return response_handler.bad_gateway(str(err))
 
@jwt_required()
def role(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check id is UUID or not
            UUID(id)
            # Check Role is exist or not
            roles = select_by_id(Roles,id)
            if roles == None:
                return response_handler.not_found('Role not Found')
            
            # Add data to response 
            schema = RolesSchema()
            data = schema.dump(roles)
            
            return response_handler.ok(data,"")
        else:
            return response_handler.unautorized()
        
    except ValueError:
        return response_handler.bad_request("Invalid Id")
        
    except Exception as err:
        return response_handler.bad_gateway(str(err))
  
@jwt_required()
def update_role(id):
    try: 
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check  id is UUID or not
            UUID(id)
            json_body = request.json
            
            # Check error with schema
            schema = RolesSchema()
            errors = schema.validate(json_body) 
            if errors:
                return response_handler.bad_request(errors)
             
            # Check role if not exist
            roles = select_by_id(Roles,id)
            if roles == None:
                return response_handler.not_found('Role not Found')
            
            # Check name of role same with previous or not
            if json_body['name'] == roles.name: 
                return response_handler.bad_request("Your Role Already Updated")
            else:
                current_role = filter_by(Roles, 'name', json_body['name'])
                # Check role same with the others or not
                if current_role != None: 
                    return response_handler.conflict('Role is exist') 
                
                # Add role to db
                roles.name = json_body['name']  
                db.session.commit()

                return response_handler.ok("", "Role successfuly updated")
        else:
            return response_handler.unautorized()

    except ValueError:
        return response_handler.bad_request("Invalid Id")
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))
 
@jwt_required()
def roles():
    try:
        current_user = get_jwt_identity() 
        
        if current_user['id_role'] in user_auth():
            # Get param from url
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
            # Check is page exceed or not
            page_exceeded = meta_data(Roles,page,per_page)
            if page_exceeded: 
                return response_handler.not_found("Page Not Found") 
            
            # Query data categories all
            roles = order_by(Roles, 'page', page, 'per_page', per_page)
            
            # Iterate to data
            data = []
            for i in roles:
                data.append({
                    "id_role" : i.id_role,
                    "name" : i.name,
                    "created_at": i.created_at,
                    "updated_at": i.updated_at
                })
                
            return response_handler.ok_with_meta(data, roles)
        else:
            return response_handler.unautorized()
        
    except Exception as err:
        return response_handler.bad_request(err)



    