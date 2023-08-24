import os, cloudinary
from cloudinary import uploader
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from uuid import UUID, uuid4
from app import db, response_handler
from app.controllers.roles import user_auth
from app.models import select_by_id, select_all, filter_by, order_by, meta_data
from app.models.books import Books, books_all,select_book_id
from app.schema.books_schema import BooksSchema
from app.schema.authors_schema import AuthorsSchema
from app.schema.publishers_schema import PublishersSchema
from app.schema.categories_schema import CategoriesSchema
from app.schema.bookshelves_schema import BookshelvesSchema
 
@jwt_required()
def create_book():
    try: 
        # Check Auth
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth(): 
            form_body = request.form
              
            # Checking errors with schema
            schema = BooksSchema() 
            errors = schema.validate(form_body)
            if errors:
                return response_handler.bad_request(errors)
            else:
                for i in select_all(Books):
                    if form_body['title'] == i.title and form_body['id_author'] == str(i.id_author):
                        return response_handler.conflict('Book is Exist')
            
            id_book = uuid4()
            new_book = Books(id_book = id_book,
                             title = form_body['title'],
                             description = form_body['description'],
                             stock = form_body['stock'],
                             id_author = form_body['id_author'],
                             id_publisher = form_body['id_publisher'],
                             id_category = form_body['id_category'],
                             id_bookshelf = form_body['id_bookshelf']
               )
            if 'picture' in request.files:
                uploadImage = request.files['picture']
                cloudinary_response = cloudinary.uploader.upload(uploadImage,
                                                    folder = "perpus-api/book-picture/",
                                                    public_id = "book_"+str(new_book.id_book),
                                                    overwrite = True,
                                                    width = 250,
                                                    height = 250, 
                                                    radius = "max",
                                                    crop = "fill"
                                                    ) 
                new_book.picture = cloudinary_response["url"]
            elif 'picture' not in request.files:
                new_book.picture = os.getenv('DEFAULT_BOOK_PICTURE')
                    
            db.session.add(new_book)
            db.session.commit()
        
            data = schema.dump(new_book)
             
            return response_handler.created(data,"Book Successfull Created ")
        else:
            return response_handler.unautorized()
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')

    except Exception as err:
        return response_handler.bad_gateway(str(err))
 
@jwt_required()
def book(id):
    try:
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check id is UUID or not
            UUID(id)
            # Check Book is exist or not
            books = select_book_id(id)
            if books == None:
                return response_handler.not_found('Book not Found')
            
            data = {"book" : BooksSchema().dump(books),
                    "author" : AuthorsSchema().dump(books.author),
                    "publisher" : PublishersSchema().dump(books.publisher),
                    "category" : CategoriesSchema().dump(books.category),
                    "bookshelf" : BookshelvesSchema().dump(books.bookshelf)}
        
            return response_handler.ok(data,"")
        else:
            return response_handler.unautorized()
        
    except ValueError:
        return response_handler.bad_request("Invalid Id")
        
    except Exception as err:
        return response_handler.bad_gateway(str(err))
  
@jwt_required()
def update_book(id):
    try: 
        current_user = get_jwt_identity()
        if current_user['id_role'] in user_auth():
            # Check  id is UUID or not
            UUID(id)
            form_body = request.form
            
            # Check error with schema
            schema = BooksSchema()
            errors = schema.validate(form_body) 
            if errors:
                return response_handler.bad_request(errors)
             
            # Check book if not exist
            books = select_by_id(Books,id)
            if books == None:
                return response_handler.not_found('Book not Found')
             
            # Check data same with previous or not
             
            if all(form_body[field] == str(getattr(books, field)) for field in ['title', 'description', 'stock', 'id_author', 'id_publisher', 'id_category', 'id_bookshelf']) and 'picture' not in request.files :
                return response_handler.bad_request("Book Already Updated")
            else:
                current_book = filter_by(Books, 'title', form_body['title'])
                # Check bookshelf same with the others or not
                if current_book != None and books.title != form_body['title']: 
                    return response_handler.conflict('Book is exist') 
                
                # Add bookshelf to db
                books.title = form_body['title']  
                books.description = form_body['description']
                books.stock = form_body['stock']
                books.id_author = form_body['id_author']
                books.id_publisher = form_body['id_publisher']
                books.id_category = form_body['id_category']
                books.id_bookshelf = form_body['id_bookshelf']
                
                if 'picture' in request.files:
                    uploadImage = request.files['picture']
                    cloudinary_response = cloudinary.uploader.upload(uploadImage,
                                                        folder = "perpus-api/book-picture/",
                                                        public_id = "book_"+str(books.id_book),
                                                        overwrite = True,
                                                        width = 250,
                                                        height = 250, 
                                                        radius = "max",
                                                        crop = "fill"
                                                        ) 
                    books.picture = cloudinary_response["url"]
                elif 'picture' not in request.files:
                    books.picture = books.picture
                    
                db.session.commit()

                return response_handler.ok("", "Book successfuly updated")
        else:
            return response_handler.unautorized()

    except ValueError:
        return response_handler.bad_request("Invalid Id")
    
    except KeyError as err:
        return response_handler.bad_request(f'{err.args[0]} field must be filled')
    
    except Exception as err:
        return response_handler.bad_gateway(str(err))
 
# @jwt_required()
# def books():
    try:
        current_user = get_jwt_identity() 
        
        if current_user['id_role'] in user_auth():
            
            # Get param from url
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
            # Check is page exceed or not
            page_exceeded = meta_data(Books,page,per_page)
            if page_exceeded: 
                return response_handler.not_found("Page Not Found") 
            
            # Query data bookshelves all
            books = order_by(Books, 'page', page, 'per_page', per_page)
            
            # Iterate to data
            data = []
            for i in books:
                data.append({
                    "id_book" : i.id_book,
                    "title" : i.title,
                    "description": i.description,
                    "stock" : i.stock,
                    "id_author" : i.id_author,
                    "id_publisher" : i.id_publisher,
                    "id_category" : i.id_category,
                    "id_bookshelf" : i.id_bookshelf,
                    "picture" : i.picture,
                    "created_at": i.created_at,
                    "updated_at": i.updated_at
                })
                
            return response_handler.ok_with_meta(data, books)
        else:
            return response_handler.unautorized()
        
    except Exception as err:
        return response_handler.bad_request(err)

def books(): 
    # Get param from url
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
    
    # Check is page exceed or not
    page_exceeded = meta_data(Books,page,per_page)
    if page_exceeded: 
        return response_handler.not_found("Page Not Found")
    
    # Query data bookshelves all
    meta = books_all('page', page, 'per_page', per_page)
     
    data = []
    for i in meta.items:
        data.append({
            "book" : BooksSchema().dump(i),
            "author" : AuthorsSchema().dump(i.author),
            "publisher" : PublishersSchema().dump(i.publisher),
            "category" : CategoriesSchema().dump(i.category),
            "bookshelf" : BookshelvesSchema().dump(i.bookshelf)
        })
          
    return response_handler.ok_with_meta(data,meta)