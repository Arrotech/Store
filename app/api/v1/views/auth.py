from flask import jsonify, request, redirect, url_for, render_template
from app.api.v1.models.models import User
from app.api.v1 import store_v1
from app.api.v1.forms.forms import UserForm, LoginForm, PasswordResetEmailForm, PasswordResetForm
from app.extensions import db
from flask_login import current_user, login_user, logout_user
from app.api.v1.services.mail import send_email
from utils.utils import default_encode_token, generate_url, default_decode_token
from arrotechtools import ErrorHandler
from werkzeug.security import generate_password_hash


@store_v1.route('/signup', methods=['POST', 'GET'])
def signup():
    """
    Create and get all users
    """
    form = UserForm()
    if form.validate_on_submit() and form.confirm_password.data == form.password.data:
        user = User(first_name=form.first_name.data,
                    middle_name=form.middle_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=form.password.data,
                    phone_number=form.phone_number.data)
        db.session.add(user)
        db.session.commit()
        token = default_encode_token(
            form.email.data, salt='email-confirm-key')
        confirm_url = generate_url(
            'store_v1.confirm_email', token=token)
        send_email.delay('Account Created Successfully',
                         sender='arrotechdesign@gmail.com',
                         recipients=[form.email.data],
                         text_body=render_template(
                                'account_created_successfully.txt', confirm_url=confirm_url),
                         html_body=render_template('account_created_successfully.html',
                                                   confirm_url=confirm_url))
        return redirect(url_for('store_v1.index'))
    return render_template('create_user.html', form=form)


@store_v1.route('/login', methods=['POST', 'GET'])
def login():
    """Already existing user can sign in to their account."""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('store_v1.dashboard'))
        return redirect(url_for('store_v1.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.role == 'admin':
                login_user(user, remember=form.remember_me.data)
                return redirect(url_for('store_v1.dashboard'))
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('store_v1.index'))

        return jsonify({'message': 'Invalid credentials'})
    return render_template('login.html', form=form)


# confirm email
@store_v1.route('/confirm_email/<token>')
def confirm_email(token):
    """
    Confirm email
    """
    try:
        email = default_decode_token(token, salt='email-confirm-key')
    except:
        return ErrorHandler.raise_error("Invalid email token", 400)
    user = User.query.filter_by(email=email).first()
    if user:
        user.email_confirmed = True
        db.session.commit()
        token = default_encode_token(
            user.email, salt='email-confirm-key')
        redirect_url = generate_url(
            'store_v1.login', token=token)
        h1 = 'Email Confirmed'
        p = 'Your email has been confirmed. You can now login to your account.'
        return render_template('success.html', redirect_url=redirect_url, h1=h1, p=p)
    return ErrorHandler.raise_error("Invalid email token", 400)

# reset password


@store_v1.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    """
    Reset password
    """
    form = PasswordResetEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = default_encode_token(
                form.email.data, salt='email-confirm-key')
            recover_url = generate_url(
                'store_v1.reset_password_with_token', token=token)
            send_email.delay('Password Reset Request',
                             sender='arrotechdesign@gmail.com',
                             recipients=[form.email.data],
                             text_body=render_template(
                                 'password_reset.txt', recover_url=recover_url),
                             html_body=render_template('password_reset.html',
                                                       recover_url=recover_url))
            h1 = 'Password Reset Request'
            p = 'A password reset link has been sent to your email.'
            return render_template('success.html', h1=h1, p=p)
    return render_template('reset_password_email_form.html', form=form)


@store_v1.route('/reset_password_with_token/<token>', methods=['POST', 'GET'])
def reset_password_with_token(token):
    """
    Reset password with token
    """
    try:
        email = default_decode_token(token, salt='email-confirm-key')
    except:
        return ErrorHandler.raise_error("Invalid email token", 400)
    user = User.query.filter_by(email=email).first()
    if user:
        form = PasswordResetForm()
        if form.validate_on_submit() and form.confirm_password.data == form.password.data:
            hashed_password = generate_password_hash(
                password=form.password.data)
            user.password = hashed_password
            db.session.commit()
            token_on_success = default_encode_token(
                user.email, salt='email-confirm-key')
            redirect_url = generate_url(
                'store_v1.login', token=token_on_success)
            send_email.delay('Password Reset Successful',
                             sender='arrotechdesign@gmail.com',
                             recipients=[user.email],
                             text_body=render_template(
                                 'password_reset_successful.txt', redirect_url=redirect_url),
                             html_body=render_template('password_reset_successful.html',
                                                       redirect_url=redirect_url))
            h1 = "Password Reset Successful"
            p = "Your password has been reset successfully. Please login to your account."
            return render_template('success.html', redirect_url=redirect_url, h1=h1, p=p)
        return render_template('reset_password.html', form=form, token=token)
    return ErrorHandler.raise_error("Invalid email token", 400)


@store_v1.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('store_v1.login'))


@store_v1.route('/user/:id', methods=['GET', 'PUT', 'DELETE', 'PATCH'])
def get_user_by_id(id):
    """
    Get user by id
    """
    if request.method == 'GET':
        return jsonify(User.get_by_id(id))
    elif request.method == 'PUT':
        user = User(request.json)
        user.update(id)
        return jsonify(user.to_dict())
    elif request.method == 'DELETE':
        user = User.get_by_id(id)
        user.delete()
        return jsonify(user.to_dict())
    elif request.method == 'PATCH':
        user = User(request.json)
        user.update(id)
        return jsonify(user.to_dict())
