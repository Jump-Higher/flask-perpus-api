import os
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID,uuid4
from app import db, response_handler
from app.controllers.roles import user_auth_user
from app.models import select_by_id, select_all, filter_by, order_by, meta_data
from app.models.cart import Carts, select_cart, select_carts, cart_all
from app.schema.carts_schema import CartsSchema
from app.schema.books_schema import BooksSchema
from app.models.borrows import Borrows
from app.models.borrow_details import BorrowDetails
  
@jwt_required()
def create_cart(id):
    try: 
        # Check Auth
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth_user(): 
                    
            new_cart = Carts(id_user = current_user['id_user'],
                            id_book = id )
                    
            db.session.add(new_cart)
            db.session.commit()
         
            return response_handler.created("","Book successfull add to cart ")
        else:
            return response_handler.unautorized()
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')

    except Exception as err:
        return response_handler.bad_gateway(str(err))
    
@jwt_required()
def co_cart(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth_user():
            UUID(id)
            cart = select_cart(id)
            id_borrow = uuid4()
            new_borrow = Borrows(id_borrow = id_borrow,
                                 return_date = None,
                                 status = False,
                                 id_user = current_user['id_user'])
            new_detail = BorrowDetails(id_borrow = id_borrow,
                                       id_book = cart.id_book)
            
            db.session.add(new_borrow)
            db.session.add(new_detail)
            db.session.commit()
            
            return response_handler.created("","Book successfull add to booking request, please contact Admin")
        else:
            return response_handler.unautorized()
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')

    except Exception as err:
        return response_handler.bad_gateway(str(err))

@jwt_required()
def carts():
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth_user():
            
            # Get param from url
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
            
            # Check is page exceed or not
            page_exceeded = meta_data(Carts,page,per_page)
            if page_exceeded: 
                return response_handler.not_found("Page Not Found")
            
            # Query data all
            meta = cart_all('page', page, 'per_page', per_page, current_user['id_user'])
            
            data = []
            for i in meta.items:
                data.append({
                    "cart" : CartsSchema().dump(i),
                    "book" : BooksSchema().dump(i.book)

                })
            return response_handler.ok_with_meta(data,meta)
                 
        return response_handler.unautorized() 
    except Exception as err:
        return response_handler.bad_gateway(str(err))
    
@jwt_required()
def delete_cart(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth_user():
            UUID(id)
            cart = select_cart(id)
            if cart == None:
                return response_handler.bad_request("Book not found")
            else:
                db.session.delete(cart)
                db.session.commit()
                return response_handler.ok("","Book is deleted from cart")
        return response_handler.unautorized()
    except ValueError:
        return response_handler.bad_request("Invalid Id")
    except Exception as err:
        return response_handler.bad_gateway(str(err))