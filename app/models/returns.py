from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class Returns(db.Model):
    __tablename__ = 'tbl_returns'
    id_return = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    return_date = db.Column(db.DateTime, default = datetime.now)
    user = db.relationship('Users', backref='tbl_returns', uselist = False)
    id_user = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_users.id_user'))
    borrow = db.relationship('Borrows', backref='tbl_returns', uselist = False)
    id_borrow = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_borrows.id_borrow'))
    created_at = db.Column(db.DateTime, default = datetime.now)
    updated_at = db.Column(db.DateTime, default = datetime.now, onupdate = datetime.now)
    