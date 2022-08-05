from unicodedata import category
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Book,Cart, Order,Note,User
from sqlalchemy import delete
from sqlalchemy.sql import func
from . import db
import json


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    bklist = db.session.query(Book).all()
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    return render_template("home.html", user=current_user, bklist=bklist,date=date)

@views.route('/show_books/<string:choice>', methods=['GET'])
@login_required
def show_books(choice):
    print("Category selected:",choice)
    if choice =="All":
        bklist = db.session.query(Book).all()
    else:
        bklist = Book.query.filter_by(category=choice).all()
    return render_template("home.html", user=current_user, bklist=bklist)


@views.route('/display_cart', methods=['GET', 'POST'])
@login_required
def display_cart():
    print("Displaying cart for user id:", current_user.id)
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    print(current_user.id)
    return render_template("display_cart.html", user=current_user,cart=cart)


@views.route('/empty-cart', methods=['POST'])
@login_required
def empty_cart():
    dele = Cart.delete().where(Cart.c.user_id==current_user.id)
    dele.execute()
    flash("Cart Empted!","warning")
    books = db.session.query(Book).all()
    return render_template("home.html", user=current_user,bklist=books)

@views.route("/delet_from_cart",methods=['GET'])
@login_required
def delete_from_cart():
    ISBN = request.args.get('ISBN')
    print("Removing book from cart with ISBN:", ISBN)
    book = Cart.query.filter_by(ISBN=ISBN,user_id= current_user.id).first()
    db.session.delete(book)
    db.session.commit()
    flash("Book removed from your cart.",'warning')
    return render_template("display_cart.html",user=current_user)


@views.route('/order_history', methods=['GET'])
@login_required
def order_history():
    if current_user.role=='manager':
        orders = Order.query.all()
        users=User.query.all()
        return render_template("order_history.html", user=current_user, users=users,orders = orders)
    else:
        return render_template("order_history.html", user=current_user, users=current_user,orders = current_user.order)

@views.route('/user_profile', methods=['GET'])
@login_required
def user_profile():
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    return render_template("user_profile.html", user=current_user,date=date)

@views.route('/manager_acc', methods=['GET', 'POST'])
@login_required
def manager_acc():
    bklist = db.session.query(Book).all()

    return render_template("manager.html", user=current_user, bklist=bklist, order = Order)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route("/aboutus")
def about_us():
    return render_template("./about_us.html",user=current_user)
