from marshmallow import Schema, fields, validate

class RolesSchema(Schema):
    
    id_role = fields.UUID(dump_only=True)
    name = fields.Str(required=True,
                      validate=[
                          validate.Length(min=2, max=100),
                          validate.Regexp(r'^[a-zA-Z\s]+$',
                                         error='Invalid name format. Only letters and space are allowed.')
                      ])
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)