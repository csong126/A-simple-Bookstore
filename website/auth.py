from cgi import print_exception
from curses.ascii import isblank
from posixpath import basename
from unicodedata import category
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Cart, User,Book, Order, Note
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

def add_manager():
    # create manager accounts
    manager = User(
        email ='manager@uab.edu',
        password = generate_password_hash('1234567', method='sha256'),
        first_name = 'Tim',
        last_name='Brown',
        role ='manager')
    manager1 = User(
        email ='manager1@uab.edu', 
        password =generate_password_hash('1234567', method='sha256'),
        first_name = 'Alex',
        last_name='Johnston',
        role ='manager')
    db.session.add(manager)
    db.session.add(manager1)
    db.session.commit()
    print("Manager accounts, manger@uab.edu and manager1@uab.edu created!")



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                if user.role=="manager":
                    print("Manager",email, 'logged in.')
                    return redirect(url_for('views.manager_acc'))
                print("a non-manger customer logged in.")
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastname')
        role ="customer"
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        print("first name:",first_name,"last name:",last_name,'password1',password1,"role",role)
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, role=role, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            m_accounts = User.query.filter_by(role='manager').all()
            if len(m_accounts)<1:
                add_manager()
            login_user(new_user, remember=True)
            if role=="manager":
                print("Manager",email, 'signed up.')
                flash('Manager account created!', category='success')
                return redirect(url_for('views.manager_acc'))
            else:    
                print("A new customer signed up.")
                flash('customer account created!', category='success')
                return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route("/add_book",methods=['POST','GET'])
@login_required
def add_book():
    if request.method=='POST':
        bname=request.form.get('bname')
        authors=request.form.get('authors')
        category=request.form.get('category')
        ISBN=request.form.get('ISBN')
        price  = request.form.get('price')
        qty = request.form.get('qty')
        new_book = Book(bname=bname,authors=authors,category=category,ISBN=ISBN,price=price,qty=qty)
        db.session.add(new_book)
        db.session.commit()
        flash('New Book Added','success')
        return redirect(url_for("views.manager_acc"))
    return redirect(url_for("views.manager_acc"))

@auth.route("/edit_book/<string:ISBN>",methods=['POST','GET'])
@login_required
def edit_book(ISBN):
    print("Editing Book:",ISBN)
    if request.method=='POST':
        price=request.form.get('price')
        stock=request.form.get('qty')
        book = Book.query.filter_by(ISBN=ISBN).first_or_404()
        book.price=price
        book.qty=stock
        db.session.commit()
        flash('Book updated','success')
        return redirect(url_for("views.manager_acc"))
    book = Book.query.filter_by(ISBN=ISBN).first_or_404()
    print("book",book)
    return render_template("edit_book.html", user=current_user,datas=book)


@auth.route("/delete_book",methods=['GET'])
def delete_book():
    ISBN = request.args.get("ISBN")
    print("Deleting book ISBN =",ISBN)
    book = Book.query.filter_by(ISBN=ISBN).first_or_404()
    db.session.delete(book)
    db.session.commit()
    flash('Book Deleted','warning')
    return redirect(url_for("views.home",user=current_user))

@auth.route("/add_to_cart/<string:ISBN>",methods=['POST','GET'])
@login_required
def add_to_cart(ISBN):
    print("add_to_cart started",ISBN)
    print(request.method)
    if request.method=='POST':
        numb = request.form.get('qty')
        book =Book.query.filter_by(ISBN=ISBN).first()
        cart_book = Cart(bname=book.bname,authors=book.authors,category=book.category,ISBN=ISBN,price=book.price,qty=numb,user_id=current_user.id)
        # check if the book already in cart
        #book_ck = Cart.query.filter_by(ISBN =ISBN,user_id = current_user.id).first()
        #if 
        db.session.add(cart_book)
        db.session.commit()
        flash("Book added sucessfully")
        return redirect(url_for("views.home",user=current_user))
    print("add_to_cart ran")
    book =Book.query.filter_by(ISBN=ISBN).first()
    return render_template("add_to_cart.html",user=current_user, book = book)


@auth.route("/checkout/<float:total>",methods=['POST','GET'])
@login_required
def checkout(total): 
    # put order infor to Order
    # reduce stock qty
    # direct to thankyou page
    print('start checkout...')
    total = round(total,2)
    if request.method=='POST':
        orders= db.session.query(Order).all()
        print("find previous orders:",orders)
        if not orders:
            order_numb = 101
        else:
            last_order=db.session.query(Order).order_by(Order.oid.desc()).first()
            print("last order number:",last_order.onumb)
            order_numb =last_order.onumb + 1
        print('Order number:', order_numb)
        for book in current_user.cart:
            bname = book.bname
            authors = book.authors
            category=book.category
            ISBN=book.ISBN
            price=book.price
            qty = book.qty
            user_id=current_user.id

            bk_stock = Book.query.filter_by(ISBN = ISBN).first_or_404()
            bk_stock.qty-=qty
            if bk_stock.qty < 1:
                flash("Sorry, there\'s no enough stock for this book: "+ bname+". Please adjust your cart.",'warning')
                return render_template("display_cart.html", user=current_user)
            else:
                item=Order(onumb=order_numb,bname=bname,authors=authors,category=category,ISBN=ISBN,price=price,qty=qty,order_total = total, user_id=user_id)
                db.session.add(item)
                db.session.commit()
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        # send a message to managers
        managers = User.query.filter_by(role="manager").all()
        for manager in managers:
            note = Note(order_number= order_numb,user_id=manager.id)
            db.session.add(note)
            db.session.commit()
            print("note added to manager",manager,manager.email)
        flash('Order completed','success')
        return render_template("thankyou.html",user=current_user)
    return render_template("checkout.html", user=current_user)



""" @auth.route("/edit_cart",methods=['POST','GET'])
@login_required
def edit_cart():
    if request.method=='POST':
        Cart.query.delete() # empty the cart first
        new_cart = request.args.get("cart")
        for book in new_cart:
            add_book=Cart(bname=book.bname,authors=book.authors,category=book.category,ISBN=book.ISBN,price=book.price,qty=book.qty)
            db.session.add(add_book)
            db.session.commit()
        flash("Cart updated sucessfully")
        return redirect(url_for("views.home",user=current_user))
    return redirect(url_for("views.home",user=current_user)) """
