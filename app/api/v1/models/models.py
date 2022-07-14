import os
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import login
from app.api.v1.views.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class User(UserMixin, db.Model):
    """User model."""

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    middle_name = db.Column(db.String(255), nullable=True)
    last_name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(255), nullable=True, unique=True)
    avatar = db.Column(db.String(100), nullable=True,
                       default=os.environ.get('AWS_DOMAIN')+"3213f4779272f3a2f4b9c137162cba84.png")
    role = db.Column(db.String(255), nullable=False, default="user")
    orders = db.relationship(
        'Order', backref='user', lazy=True,  passive_deletes=True)
    addresses = db.relationship(
        'Address', backref='user', lazy=True,  passive_deletes=True)

    def __init__(self, first_name, middle_name, last_name, email, password, phone_number):
        super().__init__()
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.email = email
        if password:
            self.password = generate_password_hash(password)
        self.phone_number = phone_number

    def check_password(self, password):
        return check_password_hash(self.password, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Product(SearchableMixin, db.Model):
    """Add Product Model."""

    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    orders = db.relationship(
        'OrderItem', backref='product', lazy=True,  passive_deletes=True)


class Address(db.Model):
    """Address Model."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(20))
    country = db.Column(db.String(20))
    zip_code = db.Column(db.Integer)
    orders = db.relationship(
        'Order', backref='address', lazy=True,  passive_deletes=True)

    def __init__(self, user_id, address, city, state, country, zip_code):
        super().__init__()
        self.user_id = user_id
        self.address = address
        self.city = city
        self.state = state
        self.country = country
        self.zip_code = zip_code


class Order(db.Model):
    """Order Model."""

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(5))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(50))
    address_id = db.Column(db.Integer, db.ForeignKey(
        'address.id', ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(10), nullable=False, default="Pending")
    payment_type = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    items = db.relationship('OrderItem', backref='order',
                            lazy=True, cascade="all, delete", passive_deletes=True)

    def order_total(self):
        """Calculate the order total."""
        return db.session.query(db.func.sum(OrderItem.quantity * Product.price)
                                ).join(Product).filter(OrderItem.order_id == self.id).scalar() + 1000

    def quantity_total(self):
        """Calculate total quantity."""
        return db.session.query(db.func.sum(OrderItem.quantity)).filter(OrderItem.order_id == self.id).scalar()


class OrderItem(db.Model):
    """Order Item Model."""

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        'order.id', ondelete="CASCADE"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id', ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Integer)
