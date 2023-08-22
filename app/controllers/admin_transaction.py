from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers.roles import user_auth
from uuid import UUID
from flask import request
from app.models.borrows import Borrows
from app.models import meta_data, select_by_id
import os
from app import response_handler,db
from app.models.borrow_details import BorrowDetails, select_all_detail
from app.schema.borrow_details_schema import BorrowDetailsSchema
from app.schema.user_schema import UserSchema 
from app.schema.books_schema import BooksSchema 
from app.models.returns import select_notin_borrow 
from app.models.returns import Returns
from app.models.return_details import ReturnDetails
from uuid import uuid4

@jwt_required()
def booked_books():
    try:
        # Check Auth
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Get param from url
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
            
            # Check is page exceed or not
            page_exceeded = meta_data(BorrowDetails,page,per_page)
            if page_exceeded: 
                return response_handler.not_found("Page Not Found")
            from app.schema.borrows_schema import BorrowsSchema
            # Query data all
            meta = select_all_detail('page', page, 'per_page', per_page)
            data = []
            for i in meta.items:
                data.append({
                    "borrow_detail" : BorrowDetailsSchema().dump(i),
                    "borrow" : BorrowsSchema().dump(i.borrow),
                    "book" : BooksSchema().dump(i.book),
                    "user" : UserSchema().dump(i.borrow.user)
                })
            return response_handler.ok_with_meta(data,meta)
                 
        return response_handler.unautorized() 
    except Exception as err:
        return response_handler.bad_gateway(str(err))
       
@jwt_required()
def acc_book(id):
    try:
        # Check Auth
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            UUID(id)
            borrows = select_by_id(Borrows,id)
            if borrows == None:
                return response_handler.not_found('Borrows not Found')
            elif borrows == True:
                return response_handler.conflict('Borrowed book already acc by Admin')
            
            borrows.status = True
            db.session.commit()
            return response_handler.ok("","Book been acc")
        return response_handler.unautorized()
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))    


def return_books():
    try:
         # Get param from url
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
        
        # Check is page exceed or not
        page_exceeded = meta_data(BorrowDetails,page,per_page)
        if page_exceeded: 
            return response_handler.not_found("Page Not Found")
        
        # Query data bookshelves all
        meta = select_notin_borrow('page', page, 'per_page', per_page)
        from app.schema.borrows_schema import BorrowsSchema
        data = []
        for i in meta.items:
            data.append({
                "borrow" : BorrowsSchema().dump(i.borrow),
                "borrow_detail" : BorrowDetailsSchema().dump(i),
                "id_user" : UserSchema().dump(i.borrow.user) ,
                "id_book" : BooksSchema().dump(i.book)
            })
        return response_handler.ok(data,"")
        
    except Exception as err:
        return response_handler.bad_gateway(err)


def create_return():
    try:
        json_body = request.json
        id_return = uuid4()
        new_return = Returns(id_return = id_return,
                             id_user = json_body['id_user'],
                             id_borrow = json_body['id_borrow'])
        new_return_detail = ReturnDetails(id_return = id_return,
                                          id_book = json_body['id_book'])
        
        db.session.add(new_return)
        db.session.add(new_return_detail)
        db.session.commit()
        
        return response_handler.ok("","sip")
        
    except:
        pass