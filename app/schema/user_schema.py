from marshmallow import Schema,validate,fields
from app.schema.roles_schema import RolesSchema


class UserSchema(Schema):
    class Meta:
        fields = ('email','name','username','password')
        
    id_user = fields.UUID(dump_only = True)
    name = fields.Str(required = True,
                          validate = [
                                validate.Length(min=2, max=100),
                                validate.Regexp(r'^[a-zA-Z\s]+$',
                                          error='Invalid name format, Only letters and space are allowed.')
                          ])
    username = fields.Str(required = True,
                              validate = [
                                    validate.Length(min=4, max=12,
                                    error='Username must be between 4 and 12 characters.')
                              ])
    email = fields.Email(required = True,
                             validate = validate.Email(error = 'Invalid email format'))
    password = fields.Str(required = True,
                              validate =[
                                    validate.Length(min=8),
                                    validate.Regexp(
                                    r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).*$',
                                    error='Password must containat least one lowercase letter, one uppercase latter, one digit, and one special character.'
                              )
                              ])
    picture = fields.Str(validate=validate.Length(max=200))
    is_active = fields.Boolean()
    created_at = fields.DateTime(dump_only = True)
    updated_at = fields.DateTime(dump_only = True)
    last_login = fields.DateTime(dump_only = True)
    id_role = fields.Nested(RolesSchema, attribute='tbl_roles', many=False, data_key='role')
        