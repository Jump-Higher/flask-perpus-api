from marshmallow import Schema, fields, validate, ValidationError,validates
import re

class PublishersSchema(Schema):
    class Meta:
        fields = ('id_publisher','name','email','phone_number','created_at','updated_at')  
         
    id_publisher = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(validate = validate.Email(error = 'Invalid email format'))
    phone_number = fields.Str(required = False,allow_none = True, allow_empty = True,
        
        validate=[
            validate.Regexp(
                r'^\+?[1-9]\d{6,14}$',
                error='Invalid phone number format. It should start with "+" (optional) followed by digits (6-14 digits allowed).'
            )
        ]
    ) 
            
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    