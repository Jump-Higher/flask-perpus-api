import uuid,os
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app import db, app
from app.models.roles import Roles
from app.hash import hash_password
from sqlalchemy.exc import IntegrityError

class User(db.Model):
    __tablename__ = 'tbl_user'
    id_user = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4())
    name = db.Column(db.String(100), nullable = False)
    username = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(250), nullable = False)
    password = db.Column(db.String(50), nullable = False)
    picture = db.Column(db.String(200))
    status = db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime, default = datetime.now)
    updated_at = db.Column(db.DateTime, default = datetime.now, onupdate = datetime.now)
    last_login = db.Column(db.DateTime)
    roles = db.relationship('Roles', backref='tbl_user', uselist = False)
    id_role = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_roles.id_role'))

def select_super_admin_user(id_role):
    select_user = User.query.filter_by(id_role = id_role).first()
    return select_user

def select_users():
    select_users = User.query.all()
    return select_users

def create_super_admin():
    with app.app_context():
        try:
            super_admin = Roles.query.filter_by(name=os.getenv('SUPER_ADMIN_ROLE')).first()
            if super_admin and not select_super_admin_user(super_admin.id_role):
                super_admin = User(username = os.getenv('SUPER_ADMIN_USERNAME'),
                                   name = os.getenv('SUPER_ADMIN_NAME'),
                                   email = os.getenv('SUPER_ADMIN_EMAIL'),
                                   password = hash_password(os.getenv('SUPER_ADMIN_PASSWORD')),
                                   status = True,
                                   picture = os.getenv('DEFAULT_PROFILE_PICTURE'),
                                   id_role = super_admin.id_role
                                   )
                db.session.add(super_admin)
                db.session.commit()
                
        except IntegrityError:
            db.session.rollback()