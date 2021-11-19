from app.extensions import db


class Product(db.Model):
    """Add Product Model."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(100), nullable=False)
    orders = db.relationship('OrderItem', backref='product', lazy=True)


class Order(db.Model):
    """Order Model."""

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(5))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    phone_number = db.Column(db.Integer)
    email = db.Column(db.String(50))
    address = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(20))
    country = db.Column(db.String(20))
    status = db.Column(db.String(10))
    payment_type = db.Column(db.String(10))
    items = db.relationship('OrderItem', backref='order', lazy=True)

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
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
