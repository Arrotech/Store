from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, HiddenField, SelectField, BooleanField, PasswordField
from flask_wtf.file import FileField, FileAllowed, DataRequired
from flask_uploads import IMAGES
from flask_babel import lazy_gettext as _l


class UserForm(FlaskForm):
    first_name = StringField('First Name')
    middle_name = StringField('Middle Name')
    last_name = StringField('Last Name')
    email = StringField('Email')
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')
    phone_number = StringField('Phone Number')
    avatar = FileField('Image', validators=[
        FileAllowed(IMAGES, 'only images are accepted.')])


class LoginForm(FlaskForm):
    email = StringField('Email')
    password = PasswordField('Password')
    remember_me = BooleanField('Remember Me')


class PasswordResetEmailForm(FlaskForm):
    email = StringField('Email')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')


class AddProduct(FlaskForm):
    """Add new product form."""

    name = StringField('Name')
    category = SelectField('Category', choices=[('Wear', 'Wear'), ('Electronics', 'Electronics'), (
        'Food', 'Food'), ('Drinks', 'Drinks'), ('Grocery', 'Grocery'), ('Furniture', 'Furniture')])
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
    user_id = HiddenField('User ID')


class UpdateStatus(FlaskForm):
    """Update status form."""

    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Complete', 'Complete'), ('Declined', 'Declined'), ('Returned', 'Returned'), ('Cancelled', 'Cancelled'), (
        'On Hold', 'On Hold'), ('Shipped', 'Shipped'), ('In Transit', 'In Transit'), ('Expired', 'Expired'), ('Fraud', 'Fraud')])


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)
