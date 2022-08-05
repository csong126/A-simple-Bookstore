from datetime import date
from email.headerregistry import UniqueSingleAddressHeader
from enum import unique
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(20))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    date = db.Column(db.DateTime(timezone=False), default=func.now())
    role = db.Column(db.String(20))
    cart = db.relationship('Cart')
    order = db.relationship('Order')
    notes = db.relationship('Note')

class Cart(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    bname=db.Column(db.String(150))
    authors = db.Column(db.String(100))
    category=db.Column(db.String(20))
    ISBN=db.Column(db.String(20))
    price  = db.Column(db.Float)
    qty = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Order(db.Model):
    oid = db.Column(db.Integer, primary_key=True)
    onumb=db.Column(db.Integer) # order number
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    bname=db.Column(db.String(150))
    authors = db.Column(db.String(100))
    category=db.Column(db.String(20))
    ISBN=db.Column(db.String(20))
    price  = db.Column(db.Float)
    qty = db.Column(db.Integer)
    order_total=db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Book(db.Model):
    bid=db.Column(db.Integer,primary_key=True)
    bname=db.Column(db.String(150))
    authors = db.Column(db.String(100))
    category=db.Column(db.String(20))
    ISBN=db.Column(db.String(20))
    price  = db.Column(db.Float)
    qty = db.Column(db.Integer)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    order_number = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # manager id