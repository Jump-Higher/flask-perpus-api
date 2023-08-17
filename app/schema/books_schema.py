
from marshmallow import Schema, fields, validate
from app.schema.authors_schema import AuthorsSchema
from app.schema.publishers_schema import PublishersSchema
from app.schema.categories_schema import CategoriesSchema
from app.schema.bookshelves_schema import BookshelvesSchema
 
class BooksSchema(Schema):
    
    id_book = fields.UUID(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=1))
    stock = fields.Int(required=True, validate=validate.Range(min=0))
    picture = fields.Str(validate=validate.Length(max=200)) 
    id_author = fields.Nested(AuthorsSchema, attribute='tbl_authors', many=False, data_key='author')
    id_publisher = fields.Nested(PublishersSchema, attribute='tbl_publisher', many=False, data_key='publisher')
    id_category = fields.Nested(CategoriesSchema, attribute = 'tbl_categories', many = False, data_key = 'category')
    id_bookshelf = fields.Nested(BookshelvesSchema, attribute = 'tbl_bookshelves', many = False, data_key = 'bookshelf' )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


 