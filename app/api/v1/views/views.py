import secrets
import random
import os
from os import path
from flask import render_template, redirect, url_for, session

from app.api.v1 import store_v1
from app.api.v1.forms.forms import AddProduct, AddToCart, Checkout
from app.api.v1.models.models import Product, Order, OrderItem
from app.extensions import db
from app.api.v1.models.models import Product


@store_v1.route('/home')
def index():
    """Home page."""
    products = Product.query.all()
    return render_template('index.html', products=products)


@store_v1.route('/dashboard')
def dashboard():
    """Home page."""
    products = Product.query.all()
    products_in_stock = Product.query.filter(Product.stock > 0).count()
    orders = Order.query.all()
    return render_template('dashboard.html', products=products, products_in_stock=products_in_stock, orders=orders)


@store_v1.route('/add-product', methods=['POST', 'GET'])
def add_product():
    """Add a new product."""
    form = AddProduct()
    if form.validate_on_submit():
        picture_file = save_picture(form.image.data)
        product = Product(name=form.name.data, price=form.price.data,
                          stock=form.stock.data, description=form.description.data, image=picture_file)

        db.session.add(product)
        db.session.commit()

        return redirect(url_for('store_v1.index'))
    return render_template('add_product.html', form=form)


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
    form = Checkout()

    products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()

    if form.validate_on_submit():

        order = Order()
        form.populate_obj(order)
        order.reference = ''.join([random.choice('ABCDE') for _ in range(5)])
        order.status = 'PENDING'

        for product in products:
            order_item = OrderItem(
                quantity=product['quantity'],
                product_id=product['id']
            )
            order.items.append(order_item)

            product = Product.query.filter_by(id=product['id']).update({"stock": Product.stock - product['quantity']})

        db.session.add(order)
        db.session.commit()
        session['cart'] = []
        session.modified = True

        return redirect(url_for('store_v1.index'))

    return render_template('checkout.html', form=form, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total)


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
