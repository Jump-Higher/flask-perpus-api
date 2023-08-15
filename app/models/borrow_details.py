from app import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

class BorrowDetails(db.Model):
    __tablename__ = 'tbl_borrow_details'
    id_borrow_detail = db.Column(UUID(as_uuid = True), primary_key = True, default = uuid.uuid4)
    borrow = db.relationship('Borrows', backref='tbl_borrow_details', uselist = False)
    id_borrow = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_borrows.id_borrow'))
    book = db.relationship('Books', backref='tbl_borrow_details', uselist = False)
    id_book = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_books.id_book'))
    created_at = db.Column(db.DateTime, default = datetime.now)
    updated_at = db.Column(db.DateTime, default = datetime.now, onupdate = datetime.now)
    