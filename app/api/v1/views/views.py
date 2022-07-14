import random
import os
from flask import render_template, redirect, url_for, session, g, request, current_app
from flask_login import current_user
from flask_babel import _, get_locale

from app.api.v1 import store_v1
from app.api.v1.forms.forms import AddProduct, AddToCart, Checkout, UpdateStatus, SearchForm, AddressForm
from app.api.v1.models.models import Product, Order, OrderItem, Address, User
from app.extensions import db
from app.api.v1.models.models import Product
from app.api.v1.services.mail import send_email
from app.api.v1.services.s3 import upload_file_to_s3
from utils.utils import default_encode_token, generate_url

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


@store_v1.before_app_request
def before_request():
    g.search_form = SearchForm()
    g.locale = str(get_locale())


@store_v1.route('/home')
def index():
    """Home page."""
    products = Product.query.all()
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return render_template('products.html', products=products, user=current_user)
        return redirect(url_for('store_v1.dashboard'))
    return render_template('products.html', products=products)


@store_v1.route('/search', methods=['POST', 'GET'])
def search():
    if not g.search_form.validate():
        return redirect(url_for('store_v1.index'))

    page = request.args.get('page', 1, type=int)
    products, total = Product.search(
        g.search_form.q.data, page, current_app.config['PRODUCTS_PER_PAGE'])
    next_url = url_for('store_v1.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['PRODUCTS_PER_PAGE'] else None
    prev_url = url_for('store_v1.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), next_url=next_url, prev_url=prev_url, products=products)


@store_v1.route('/order-items')
def order_items():
    """Home page."""
    order_items = OrderItem.query.all()
    products = Product.query.all()
    orders = Order.query.all()
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return render_template('order_items.html', order_items=order_items, products=products, orders=orders, user=current_user)
        return redirect(url_for('store_v1.dashboard'))
    return redirect(url_for('store_v1.index'))


# get specific order items
@store_v1.route('/order-items/<int:id>')
def order_item(id):
    """Home page."""
    order_item = OrderItem.query.filter_by(id=id).first()
    product = Product.query.filter_by(id=order_item.product_id).first()
    order = Order.query.filter_by(id=order_item.order_id).first()
    address = Address.query.filter_by(id=order.address_id).first()
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return render_template('user-order-detail.html', order_item=order_item, user=current_user, product=product, order=order, address=address)
        return redirect(url_for('store_v1.dashboard'))
    return redirect(url_for('store_v1.index'))


@store_v1.route('/dashboard')
def dashboard():
    """Home page."""
    add_product_form = AddProduct()
    update_status_form = UpdateStatus()
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            products = Product.query.all()
            products_in_stock = Product.query.filter(Product.stock > 0).count()
            orders = Order.query.all()
            return render_template('dashboard.html',  add_product_form=add_product_form, update_status_form=update_status_form, products=products, products_in_stock=products_in_stock, orders=orders, user=current_user)
        return redirect(url_for('store_v1.index'))
    return redirect(url_for('store_v1.login'))


@store_v1.route('/add-product', methods=['POST', 'GET'])
def add_product():
    """Add a new product."""
    error_message = ''
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            form = AddProduct()
            if form.validate_on_submit():
                picture_file = upload(form.image.data)
                product = Product(name=form.name.data, category=form.category.data, price=form.price.data,
                                  stock=form.stock.data, description=form.description.data, image=os.environ.get('AWS_DOMAIN')+picture_file)
                db.session.add(product)
                db.session.commit()
                return render_template('add_product.html', form=form, user=current_user, success_message='Product added successfully')
            return render_template('add_product.html', form=form, user=current_user, error_message=error_message)
        return redirect(url_for('store_v1.index'))
    return redirect(url_for('store_v1.login'))


@store_v1.route('/product/<int:id>')
def get_product(id):
    form = AddProduct()
    product = Product.query.filter_by(id=id).first()
    return render_template('product.html', product=product, user=current_user, form=form)


# get product by category
@store_v1.route('/category/<string:category>')
def get_products_by_category(category):
    products = Product.query.filter_by(category=category).all()
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return render_template('products.html', products=products, user=current_user)
        return redirect(url_for('store_v1.dashboard'))
    return render_template('products.html', products=products)


@store_v1.route('/view-product/<id>', methods=['POST', 'GET'])
def product(id):
    """View single product."""
    product = Product.query.filter_by(id=id).first()
    form = AddToCart()
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return render_template('view-product.html', product=product, form=form, user=current_user)
        return redirect(url_for('store_v1.dashboard'))
    return render_template('view-product.html', product=product, form=form)


@store_v1.route('/update-product/<int:id>', methods=['POST', 'GET'])
def update_product(id):
    """Update a product."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            product = Product.query.filter_by(id=id).first()
            add_product_form = AddProduct()
            if add_product_form.validate_on_submit():
                if add_product_form.image.data:
                    picture_file = upload(add_product_form.image.data)
                    product.image = os.environ.get('AWS_DOMAIN')+picture_file
                product.name = add_product_form.name.data
                default_category = 'No category'
                product.category = request.form.get(
                    'category', default_category)
                product.price = add_product_form.price.data
                product.stock = add_product_form.stock.data
                default_description = 'No description'
                product.description = request.form.get(
                    'description', default_description)
                db.session.commit()
                message = "Product added successfully"
                return render_template('product.html', product=product, user=current_user, form=add_product_form, success_message=message)
            return render_template('product.html', product=product, user=current_user, form=add_product_form)
        return redirect(url_for('store_v1.index'))
    return redirect(url_for('store_v1.login'))


@store_v1.route('/delete-product/<id>', methods=['POST', 'GET'])
def delete_product(id):
    """Delete a product."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            product = Product.query.filter_by(id=id).first()
            db.session.delete(product)
            db.session.commit()
            return redirect(url_for('store_v1.dashboard'))
        return redirect(url_for('store_v1.index'))
    return redirect(url_for('store_v1.login'))


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
    if current_user.is_authenticated:
        if current_user.role == 'user':
            return render_template('cart.html', products=products, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total, user=current_user)
        return redirect(url_for('store_v1.dashboard'))
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
                addresses = Address.query.filter_by(
                    user_id=current_user.id).all()
                form = Checkout()
                products, grand_total, grand_total_plus_shipping, quantity_total = handle_cart()
                if form.validate_on_submit():
                    order = Order()
                    form.populate_obj(order)
                    order.reference = ''.join(
                        [random.choice('ABCDE') for _ in range(5)])
                    default_address = 'No address'
                    address = request.form.get(
                        'address', default_address)
                    address_to_be_added = Address.query.filter_by(
                        address=address).first()
                    order.address_id = address_to_be_added.id

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

                return render_template('checkout.html', form=form, addresses=addresses, grand_total=grand_total, grand_total_plus_shipping=grand_total_plus_shipping, quantity_total=quantity_total, user=current_user)
            h1 = "Bad request"
            p = "Please confirm your email address first before you checkout this order."
            return render_template('errors.html', h1=h1, p=p)
    return redirect(url_for('store_v1.login'))


@store_v1.route('/update-status/<id>', methods=['POST'])
def update_status(id):
    """Update status of order."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            order = Order.query.filter_by(id=id).first()
            update_status_form = UpdateStatus()
            if update_status_form.validate_on_submit():
                order.status = update_status_form.status.data
                db.session.commit()
                return redirect(url_for('store_v1.dashboard'))
            return render_template('dashboard.html', update_status_form=update_status_form, order=order)
        return redirect(url_for('store_v1.index'))
    return redirect(url_for('store_v1.login'))


@store_v1.route('/view-order/<order_id>')
def view_order(order_id):
    order = Order.query.filter_by(id=int(order_id)).first()
    address = Address.query.filter_by(id=order.address_id).first()
    user = User.query.filter_by(id=order.user_id).first()
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return render_template('view-order.html', order=order, address=address, user=user)
        return render_template('user-order.html', order=order, user=current_user, address=address)
    return redirect(url_for('store_v1.login'))

# delete order by id
@store_v1.route('/delete-order/<order_id>')
def delete_order(order_id):
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            order = Order.query.filter_by(id=int(order_id)).first()
            db.session.delete(order)
            db.session.commit()
            return redirect(url_for('store_v1.dashboard'))
        return redirect(url_for('store_v1.index'))
    return redirect(url_for('store_v1.login'))


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


@store_v1.route('/addresses')
def addresses():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            addresses = Address.query.filter_by(user_id=current_user.id).all()
            return render_template('addresses.html', addresses=addresses, user=current_user)
        return redirect(url_for('store_v1.dashboard'))
    return redirect(url_for('store_v1.login'))


@store_v1.route('/add-address', methods=['GET', 'POST'])
def add_address():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            form = AddressForm()
            if form.validate_on_submit():
                address = Address(
                    address=form.address.data,
                    city=form.city.data,
                    state=form.state.data,
                    country=form.country.data,
                    zip_code=form.zip_code.data,
                    user_id=current_user.id,
                )
                db.session.add(address)
                db.session.commit()
                return redirect(url_for('store_v1.addresses'))
            return render_template('add_new_address.html', form=form, user=current_user)
        return redirect(url_for('store_v1.dashboard'))
    return redirect(url_for('store_v1.login'))


@store_v1.route('/edit-address/<id>', methods=['GET', 'POST'])
def edit_address(id):
    if current_user.is_authenticated:
        if current_user.role == 'user':
            address = Address.query.filter_by(id=id).first()
            form = AddressForm()
            if form.validate_on_submit():
                address.address = form.address.data
                address.city = form.city.data
                address.state = form.state.data
                address.country = form.country.data
                address.zip_code = form.zip_code.data
                db.session.commit()
                return redirect(url_for('store_v1.addresses'))
            return render_template('edit_address.html', form=form, address=address)
        return redirect(url_for('store_v1.dashboard'))
    return redirect(url_for('store_v1.login'))


@store_v1.route('/delete-address/<id>')
def delete_address(id):
    if current_user.is_authenticated:
        if current_user.role == 'user':
            address = Address.query.filter_by(id=id).first()
            db.session.delete(address)
            db.session.commit()
            return redirect(url_for('store_v1.addresses'))
        return redirect(url_for('store_v1.dashboard'))
    return redirect(url_for('store_v1.login'))


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload(filedata):
    if filedata and allowed_file(filedata.filename):
        picture_fn = upload_file_to_s3(filedata)
        return picture_fn
