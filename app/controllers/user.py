from flask import request
from app.schema.user_schema import UserSchema, PasswordSchema
from app.schema.roles_schema import RolesSchema
from app.schema.address_schema import AddressSchema
from app import response_handler,db,secret_key
from app.models.users import  Users, select_by_id,user_all, select_user_email
from app.models.roles import select_role_id, super_admin_role, admin_role
from app.hash import hash_password
from flask_jwt_extended import jwt_required,get_jwt_identity
import os, cloudinary
from uuid import uuid4
from app.models import select_all,meta_data
from app.models.addresses import Addresses, select_user_address
from datetime import datetime
from app.controllers.roles import user_auth
from app.controllers import generate_token, send_email, reset_password_body, activation_body
from uuid import UUID
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


def register():
    try:
        json_body = request.json
        user_schema = UserSchema()
        
        # checking errors with schema
        errors = user_schema.validate(json_body, partial=('name', 'username', 'email', 'password'))
        if errors:
            return response_handler.bad_request(errors)
        else:
            for i in select_all(Users):
                if json_body['username'] == i.username or json_body['email'] == i.email:
                    return response_handler.bad_request("Username or email is exist")
          
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

@jwt_required()
def user(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth() or current_user['id_user'] == str(id):
            # Check id is UUID or not
            UUID(id)
            # Check user is exist or not
            from app.models.users import select_user_id
            users = select_user_id(id)
            if users == None:
                return response_handler.not_found('User not Found')
            
            data = {"user" : UserSchema().dump(users),
                    "address" : AddressSchema().dump(users.address),
                    "role" : RolesSchema().dump(users.role)}
            
            return response_handler.ok(data,"")
        else:
            return response_handler.unautorized()
        
    except ValueError:
        return response_handler.bad_request("Invalid Id")
        
    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()  
def update_user(id):
    try:
        
        current_user = get_jwt_identity()
        if current_user['id_user'] == id:
            # Check  id is UUID or not
            UUID(id)
            form_body = request.form
            
            # Select formbody to check
            user_data = {'username':form_body['username'],
                    'email':form_body['email'],
                    'password':form_body['password'],
                    'name':form_body['name']}
            address_data = {'address': form_body['address']}
            
            # Check error with schema
            user_schema = UserSchema(only=['username','name','email','password'])
            address_schema = AddressSchema()

            user_errors = user_schema.validate(user_data)
            address_errors = address_schema.validate(address_data)
            if user_errors: 
                return response_handler.bad_request(user_errors)
            if address_errors:
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
            return response_handler.unautorized()

    except ValueError:
        return response_handler.bad_request("Invalid Id")
    
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
             # Get param from url
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
            
            # Check is page exceed or not
            page_exceeded = meta_data(Users,page,per_page)
            if page_exceeded: 
                return response_handler.not_found("Page Not Found")
            # Query data bookshelves all
            meta = user_all('page', page, 'per_page', per_page)
            data = []
            for i in meta.items:
                data.append({
                    "user" : UserSchema().dump(i),
                    "address" : AddressSchema().dump(i.address),
                    "role" : RolesSchema().dump(i.role)
                })
                
            return response_handler.ok_with_meta(data,meta)
        else:
            return response_handler.unautorized("You are not Allowed here")
    except Exception as err:
        return response_handler.bad_gateway(str(err))
  
def reset_password():
    try:
        json_body = request.json
        email = json_body['email']
        user = select_user_email(email) 
        if user == None:
            return response_handler.bad_request("User not found")
        
        # Generate Token
        token = generate_token(email)
        # Replace . with | 
        reset_token = token.replace('.','|')
        # Add html url
        reset_url = os.getenv('RESET_PASSWORD_FE')+'/'+reset_token
        reset_body = reset_password_body(reset_url,user.name)
        
        #Send mail
        send_email(email,"Reset Password",reset_body)
        
        return response_handler.ok("","Please check your email to reset your password")
    except Exception as err:
        return response_handler.bad_gateway(str(err))

def change_password(token):
    try:
        json_body = request.json
        serializer = URLSafeTimedSerializer(secret_key)
        reset_token = token.replace('|','.')
        email = serializer.loads(reset_token, max_age=os.getenv('MAX_AGE_MAIL'))  # Token expires after 1 hour (3600 seconds)
        user = select_user_email(email)
        if user:
            password_schema = PasswordSchema()
            errors = password_schema.validate(json_body)
            if errors:
                return response_handler.bad_request(errors)
            user.password = hash_password(json_body['password'])
            db.session.commit()
            return response_handler.ok("","Your password success to change")
        else:
            return response_handler.not_found("Account not found")
    except SignatureExpired:
        return response_handler.unautorized("Your Token is Expired")
    except BadSignature:
        return response_handler.bad_request("Your Token is Invalid")
    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()
def activation_email():
    try:
        current_user = get_jwt_identity()
        user = select_by_id(current_user['id_user'])
        token = generate_token(user.email)
        activation_token = token.replace('.','|')
        # Add html url
        #activation_url = os.getenv('ACTIVATION_ACC_FE')+'/'+activation_token
        activation_url = "www.yahoo.com"
        activate_body = activation_body(activation_url,user.username)
        #Send mail
        send_email(user.email,"Activation Account",activate_body)
        
        return response_handler.ok("","Please check your email to activate your account")
    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()
def activation_account(token): 
    serializer = URLSafeTimedSerializer(secret_key)
    activation_token = token.replace('|','.')
    email = serializer.loads(activation_token, max_age=os.getenv('MAX_AGE_MAIL'))  # Token expires after 1 hour (3600 seconds)
    user = select_user_email(email)
    user.status = True
    db.session.commit()
    return response_handler.ok("","Your Account success to activate")
    