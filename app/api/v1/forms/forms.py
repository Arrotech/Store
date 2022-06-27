from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField, SelectField, BooleanField
from flask_wtf.file import FileField, FileAllowed
from flask_uploads import IMAGES


class UserForm(FlaskForm):
    first_name = StringField('First Name')
    middle_name = StringField('Middle Name')
    last_name = StringField('Last Name')
    email = StringField('Email')
    password = StringField('Password')
    confirm_password = StringField('Confirm Password')
    phone_number = StringField('Phone Number')


class LoginForm(FlaskForm):
    email = StringField('Email')
    password = StringField('Password')
    remember_me = BooleanField('Remember Me')


class AddProduct(FlaskForm):
    """Add new product form."""

    name = StringField('Name')
    price = IntegerField('Price')
    stock = IntegerField('Quantity')
    description = TextAreaField('Description')
    image = FileField('Image', validators=[
                      FileAllowed(IMAGES, 'only images are accepted.')])


class AddToCart(FlaskForm):
    """Add to cart form."""

    quantity = IntegerField('Quantity')
    id = HiddenField('ID')


class Checkout(FlaskForm):
    """Checkout form."""

    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    phone_number = StringField('Phone Number')
    email = StringField('Email')
    address = StringField('Address')
    city = StringField('City')
    state = SelectField('State', choices=[('NAK', 'Nakuru'), ('NAI', 'Nairobi'), (
        'MOM', 'Mombasa'), ('KIS', 'Kisumu'), ('KAK', 'Kakamega')])
    country = SelectField('Country', choices=[(
        'KE', 'Kenya'), ('USA', 'United States'), ('UK', 'United Kingdom'), ('CHI', 'China')])
    payment_type = SelectField('Payment Type', choices=[
                               ('CK', 'Check'), ('WT', 'Wire Transfer')])
