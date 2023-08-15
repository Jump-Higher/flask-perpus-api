from flask import request
from app.schema.user_schema import UserSchema
from app.schema.roles_schema import RolesSchema
from app.schema.address_schema import AddressSchema
from app import response_handler,db
from app.models.users import select_users, Users, select_by_id
from app.models.roles import select_role_id, super_admin_role, admin_role
from app.hash import hash_password
from flask_jwt_extended import jwt_required,get_jwt_identity
import os, cloudinary
from uuid import uuid4
from app.models.addresses import Addresses, select_user_address
from datetime import datetime

def register():
    try:
        json_body = request.json
        user_schema = UserSchema()
        
        # checking errors with schema
        errors = user_schema.validate(json_body, partial=('name', 'username', 'email', 'password'))
        if errors:
            return response_handler.bad_request(errors)
            
        # iterasi tbl_user
        list = []
        for i in select_users():
            list.append({
                "username": i.username,
                "email": i.email
            })
            
        # validate if username and email is exist
        for i in list:
            if json_body['username'] == i['username']:
                return response_handler.conflict('Username is Exist')
            elif json_body['email'] == i['email']:
                return response_handler.conflict('Email is Exist')
        
        id_address = uuid4()
        address = Addresses(id_address = id_address)
        
        new_user = Users(username = json_body['username'],
                        name = json_body['name'],
                        email = json_body['email'],
                        password = hash_password(json_body['password']),
                        picture = os.getenv('DEFAULT_PROFILE_PICTURE'),
                        id_role = select_role_id(os.getenv('USER_ROLE')),
                        id_address = id_address
                        )
        db.session.add(address)
        db.session.add(new_user)
        db.session.commit()
        
        user_schema = UserSchema(only=('id_user', 'name', 'username', 'email', 'password', 'created_at'))
        data = user_schema.dump(new_user)

        return response_handler.created(data, "User registered successfully")
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))

def user(id):
    try:
        # Check user is exist or not
        select_user = select_users()
        exist = False
        for i in select_user:
            if(str(i.id_user) == id):
                exist = True
                break
            elif not select_user:
                break
        if not exist:
            return response_handler.not_found('User Not Found')
        
        # Add data user to response
        user = select_by_id(id)
        user_schema = UserSchema()
        data = user_schema.dump(user)
        
        # Add data user roles to response
        role = user.roles
        role_schema = RolesSchema()
        role_data = role_schema.dump(role)
        data['role'] = role_data
        
        # Add data user address to response
        address_schema = AddressSchema()
        address = user.address
        address_data = address_schema.dump(address)
        data['address'] = address_data
        
        return response_handler.ok(data,"")
        
    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()  
def update_user(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_user'] == str(id):
            form_body = request.form
            user_schema = UserSchema()
            address_schema = AddressSchema()
            address_data = {'address': form_body['address']}
            
            # Checking Error with schema
            errors = user_schema.validate(form_body) 
            address_errors = address_schema.validate(address_data)
            if errors:
                return response_handler.bad_request(errors)
            elif address_errors:
                return response_handler.bad_request(address_errors)
            
            # Select user by id
            user = select_by_id(id)
            # Select address by id
            address = select_user_address(str(user.id_address))
             
            # Check username is exist or not
            if form_body['username'] == user.username:
                user.username = form_body['username']
            else:
                existing_user = Users.query.filter_by(username=form_body['username']).first()
                if existing_user:
                    return response_handler.conflict('Username already exists')
                
            # Update user
            user.name = form_body['name']
            user.username = form_body['username']
            user.email = form_body['email']
            user.password = hash_password(form_body['password'])
            user.updated_at = datetime.now()

            # Update address
            address.address = form_body['address']
             
            if 'picture' in request.files:
                uploadImage = request.files['picture']
                cloudinary_response = cloudinary.uploader.upload(uploadImage,
                                                    folder = "perpus-api/user-profile-picture/",
                                                    public_id = "user_"+str(user.id_user),
                                                    overwrite = True,
                                                    width = 250,
                                                    height = 250,
                                                    grafity = "face",
                                                    radius = "max",
                                                    crop = "fill"
                                                    ) 
                user.picture = cloudinary_response["url"]
            elif 'picture' not in request.files:
                user.picture = user.picture

            db.session.commit()
            
            return response_handler.ok("", "Your data is updated")
        else:
            return response_handler.unautorized("You are not Allowed here")

    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()
def list_user():
    try:
        super_admin = super_admin_role()
        admin = admin_role()
        current_user = get_jwt_identity()
        if current_user['id_role'] == str(super_admin) or current_user['id_role'] == str(admin):
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 5, type=int )
            total_user = Users.query.count()
            if not per_page:
                per_page = total_user

        
            total_page = (total_user-1+per_page)//per_page
            if (page <= 0 or page > total_page ):
                response= {
                    "code": "404",
                    "status": "NOT_FOUND",
                    "errors": "page cannot negative value or more than total page",
                    "data": {
                        "total_page": total_page
                    }
                }
                return response_handler.not_found(response)

            user = Users.query.order_by(Users.created_at.desc()).paginate(page = page, per_page = per_page)
            data = []
            for i in user.items:
                data.append({
                    "id_user": i.id_user,
                    "name": i.name,
                    "username": i.username,
                    "email": i.email,
                    "password": i.password,
                    "picture" : i.picture,
                    "status" : i.status,
                    "created_at" : i.created_at,
                    "updated_at" : i.updated_at,
                    "address":{
                        "id_address": i.address.id_address,
                        "address": i.address.address
                    },
                    "role":{
                        "id_role": i.roles.id_role,
                        "role": i.roles.name
                    }
                })
            meta = {
                "page": user.page,
                "pages": user.pages,
                "total_count": user.total,
                "prev_page": user.prev_num,
                "next_page": user.next_num,
                "has_prev": user.has_prev,
                "has_next": user.has_next
            }
            return response_handler.ok_with_meta(data,meta)
        else:
            return response_handler.unautorized("You are not Allowed here")
    except Exception as err:
        return response_handler.bad_gateway(str(err))
 