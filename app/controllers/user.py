from flask import request
from app.schema.user_schema import UserSchema
from app import response_handler,db
from app.models.user import select_users, User
from app.models.roles import select_role_id
from app.hash import hash_password
import os 


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
            
        new_user = User(username = json_body['username'],
                        name = json_body['name'],
                        email = json_body['email'],
                        password = hash_password(json_body['password']),
                        picture = os.getenv('DEFAULT_PROFILE_PICTURE'),
                        id_role = select_role_id(os.getenv('USER_ROLE'))
                        )
        db.session.add(new_user)
        db.session.commit()
        
        data = user_schema.dump(new_user)
        
        return response_handler.created(data, "User registered successfully")
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))
        