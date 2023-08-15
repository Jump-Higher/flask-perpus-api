import uuid,os
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app import db, app
from app.models.roles import Roles
from app.models.addresses import Addresses
from app.hash import hash_password
from sqlalchemy.exc import IntegrityError

class Users(db.Model):
    __tablename__ = 'tbl_users'
    id_user = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    name = db.Column(db.String(100), nullable = False)
    username = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(250), nullable = False)
    password = db.Column(db.String(50), nullable = False)
    picture = db.Column(db.String(200))
    status = db.Column(db.Boolean, default = False)
    roles = db.relationship('Roles', backref='tbl_users', uselist = False)
    id_role = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_roles.id_role'))
    address = db.relationship('Addresses', backref='tbl_users', uselist = False)
    id_address = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_addresses.id_address'))
    created_at = db.Column(db.DateTime, default = datetime.now)
    updated_at = db.Column(db.DateTime, default = datetime.now)
    last_login = db.Column(db.DateTime)
    

def select_super_admin_user(id_role):
    select_user = Users.query.filter_by(id_role = id_role).first()
    return select_user

def select_users():
    select_users = Users.query.all()
    return select_users

# object
def select_by_id(id_user):
    select_user = Users.query.get(id_user)
    return select_user
 
def create_super_admin():
    with app.app_context():
        try:
            super_admin = Roles.query.filter_by(name=os.getenv('SUPER_ADMIN_ROLE')).first()
            if super_admin and not select_super_admin_user(super_admin.id_role):
                
                # Make Address for Super Admin
                id_address = uuid.uuid4()
                super_address = Addresses(id_address = id_address)
                db.session.add(super_address)
                db.session.commit()
                
                # Make Super Admin 
                super_admin = Users(username = os.getenv('SUPER_ADMIN_USERNAME'),
                                   name = os.getenv('SUPER_ADMIN_NAME'),
                                   email = os.getenv('SUPER_ADMIN_EMAIL'),
                                   password = hash_password(os.getenv('SUPER_ADMIN_PASSWORD')),
                                   status = True,
                                   picture = os.getenv('DEFAULT_PROFILE_PICTURE'),
                                   id_role = super_admin.id_role,
                                   id_address = id_address
                                   )
                db.session.add(super_admin)
                db.session.commit()
                
        except IntegrityError:
            db.session.rollback()
        except:
            pass