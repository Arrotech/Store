import secrets
import random
import os
from os import path
from flask import render_template, redirect, url_for, session
from flask_login import current_user
from arrotechtools import ErrorHandler

from app.api.v1 import store_v1
from app.api.v1.forms.forms import AddProduct, AddToCart, Checkout
from app.api.v1.models.models import Product, Order, OrderItem
from app.extensions import db
from app.api.v1.models.models import Product
from app.api.v1.services.mail import send_email
from utils.utils import default_encode_token, generate_url



@store_v1.route('/home')
def index():
    """Home page."""
    products = Product.query.all()
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return render_template('index.html', products=products, first_name=current_user.first_name)
        return redirect(url_for('store_v1.dashboard'))
    return render_template('index.html', products=products)


@store_v1.route('/dashboard')
def dashboard():
    """Home page."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            products = Product.query.all()
            products_in_stock = Product.query.filter(Product.stock > 0).count()
            orders = Order.query.all()
            return render_template('dashboard.html', products=products, products_in_stock=products_in_stock, orders=orders, first_name=current_user.first_name)
        return redirect(url_for('store_v1.index'))
    return redirect(url_for('store_v1.login'))


@store_v1.route('/add-product', methods=['POST', 'GET'])
def add_product():
    """Add a new product."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            form = AddProduct()
            if form.validate_on_submit():
                picture_file = save_picture(form.image.data)
                product = Product(name=form.name.data, price=form.price.data,
                                stock=form.stock.data, description=form.description.data, image=picture_file)

                db.session.add(product)
                db.session.commit()

                return redirect(url_for('store_v1.index'))
            return render_template('add_product.html', form=form)
        return redirect(url_for('store_v1.index'))
    return redirect(url_for('store_v1.login'))


@store_v1.route('/product/<id>', methods=['POST', 'GET'])
def product(id):
    """View single product."""
    product = Product.query.filter_by(id=id).first()
    form = AddToCart()
    return render_template('view-product.html', product=product, form=form)


@store_v1.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add product to cart."""
    if 'cart' not in session:
        session['cart'] = []
    form = AddToCart()
    if form.validate_on_submit():
        session['cart'].append(
            {"id": form.id.data, "quantity": form.quantity.data})
        session.modified = True
    return redirect(url_for('store_v1.index'))


@store_v1.route('/quick-add/<id>')
def quick_add(id):
    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({"id": id, "quantity": 1})
    session.modified = True

    return redirect(url_for('store_v1.index'))


@store_v1.route('/cart')
def cart():
    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
    return render_template('cart.html', products=products, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)


@store_v1.route('/remove-from-cart/<index>')
def remove_from_cart(index):
    del session['cart'][int(index)]
    session.modified = True
    return redirect(url_for('store_v1.cart'))


@store_v1.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page."""
    if current_user.is_authenticated:
        if current_user.role == 'user':
            if current_user.email_confirmed == True:
                form = Checkout()
                products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
                if form.validate_on_submit():
                    order = Order()
                    form.populate_obj(order)
                    order.reference = ''.join(
                        [random.choice('ABCDE') for _ in range(5)])
                    order.status = 'PENDING'

                    for product in products:
                        order_item = OrderItem(
                            quantity=product['quantity'],
                            product_id=product['id']
                        )
                        order.items.append(order_item)

                        product = Product.query.filter_by(id=product['id']).update(
                            {"stock": Product.stock - product['quantity']})

                    db.session.add(order)
                    db.session.commit()
                    session['cart'] = []
                    session.modified = True
                    token = default_encode_token(
                        current_user.email, salt='email-confirm-key')
                    confirm_url = generate_url(
                        'store_v1.login', token=token)
                    send_email.delay('Order Placed Successfully',
                                    sender='arrotechdesign@gmail.com',
                                    recipients=[current_user.email],
                                    text_body=render_template(
                                        'order_successfully_placed.txt', confirm_url=confirm_url),
                                    html_body=render_template('order_successfully_placed.html',
                                                            confirm_url=confirm_url))

                    return redirect(url_for('store_v1.index'))

                return render_template('checkout.html', form=form, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total, first_name=current_user.first_name, last_name=current_user.last_name, email=current_user.email, phone_number=current_user.phone_number)
            h1 = "Bad request"
            p = "Please confirm your email address first before you checkout this order."
            return render_template('errors.html', h1=h1, p=p)
    return redirect(url_for('store_v1.login'))


@store_v1.route('/view-order/<order_id>')
def view_order(order_id):
    order = Order.query.filter_by(id=int(order_id)).first()
    return render_template('view-order.html', order=order)


def save_picture(form_picture):
    """Save an image."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    basedir = path.abspath(path.dirname('requirements.txt'))
    picture_path = os.path.join(basedir, 'static/images/products', picture_fn)
    form_picture.save(picture_path)
    return picture_fn


def handle_cart():
    products = []
    grand_total = 0
    index = 0
    quantity_total = 0
    for item in session['cart']:
        product = Product.query.filter_by(id=item['id']).first()
        quantity = int(item['quantity'])
        total = quantity * product.price
        grand_total += total
        quantity_total += quantity

        products.append({"id": product.id, "name": product.name, "price": product.price,
                        "image": product.image, "quantity": quantity, "total": total, "index": index})
        index += 1

    grand_total_plus_shipping = grand_total + 1000
    return products, grand_total, grand_total_plus_shipping, quantity_total
