
from marshmallow import Schema, fields, validate
import uuid
class BooksSchema(Schema):
    
    id_bookshelf = fields.UUID(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=1))
    stock = fields.Int(required=True, validate=validate.Range(min=0))
    picture = fields.Str(required=True, validate=validate.Length(min=1))
    bookshelf = fields.Str(required=True,
                      validate=[
                        validate.Length(min=2, max=100),
                        validate.Regexp(
                            r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d\s]+$',
                            error='Invalid name format. Only letters, space, and at least one number are allowed.'
                        )
                    ])
    id_author = fields.UUID(required=True )
    id_publisher = fields.UUID(required=True )
    id_category = fields.UUID(required=True )
    id_bookshelf = fields.UUID(required=True )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


 