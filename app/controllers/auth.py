from datetime import datetime
from flask import request
# from flask_jwt_extended import decode_token
from app import db, response_handler
from app.models.users import Users
from app.hash import hash_password
from app.generate_token import generate_token

def login():
    try:        
        json_body = request.json        
        if json_body['username'] =="":
            return response_handler.bad_request("Username must be filled")
        
        if json_body['password'] =="":
            return response_handler.bad_request("Password must be filled")
        
        user = Users.query.filter_by(username = json_body['username']).first()
    
        if not user:
            return response_handler.not_found("Username not found")
        
        if hash_password(json_body['password']) != user.password:
            return response_handler.unautorized_login()
        
        user.last_login = datetime.now()
        db.session.commit()
        data = generate_token({"id_user":user.id_user,
                                "id_role":user.id_role, 
                                "role":user.role.name}
                              )
        user = {"id_user": user.id_user,
                "id_role": user.id_role,
                "role": user.role.name,
                "status": user.status}
        data['data'] = user
        # decode token
        # print(decode_token(token['token']['access_token']))
        # decode = (decode_token(token['token']['access_token']))
        # print(decode['sub']['role'])
        return response_handler.ok(data, message='Login successful, have a nice day')
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    except Exception as err:
        return response_handler.bad_gateway(err)