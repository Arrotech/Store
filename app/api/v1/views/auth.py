from flask import jsonify, request, redirect, url_for, render_template
from app.api.v1.models.models import User
from app.api.v1 import store_v1
from app.api.v1.forms.forms import UserForm, LoginForm
from app.extensions import db
from flask_jwt_extended import create_access_token
from flask_login import current_user, login_user, logout_user


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
